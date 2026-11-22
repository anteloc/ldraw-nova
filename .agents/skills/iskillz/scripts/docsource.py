"""Get API docs as a markdown tree, whatever form they are published in.

Sources:
  local path    a root .md/.rst/.html file or a docs folder
  git           a repo URL, or a GitHub/GitLab .../tree|blob/<ref>/<path> URL
                (sparse, shallow checkout of just the docs folder)
  website       a docs page URL (e.g. a Sphinx or mkdocs site): the pages its
                sidebar nav lists are downloaded (or, without a nav, the pages
                linked below the start page's folder)

Everything fetched lives in <out>/fetch/ (the only folder `fetch` ever
replaces). Markdown sources are used as they are. reStructuredText (Sphinx)
and HTML are converted to markdown with pandoc into <out>/fetch/docs/, and
the hierarchy (Sphinx toctrees, or the site's sidebar nav) is written as a
mkdocs-style nav in <out>/fetch/mkdocs.yml, so `map` picks the authors' own
hierarchy up.
"""

from __future__ import annotations

import fnmatch
import json
import os
import posixpath
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml


class Error(Exception):
    """A user-facing failure: printed without a traceback."""


class MkdocsLoader(yaml.SafeLoader):
    """SafeLoader that tolerates mkdocs tags such as !ENV and !!python/name."""


for _prefix in ("!", "tag:yaml.org,2002:python/"):
    MkdocsLoader.add_multi_constructor(_prefix, lambda loader, suffix, node: None)


USER_AGENT = "Mozilla/5.0 (compatible; skilltree-docs-fetcher)"
GIT_URL_RE = re.compile(
    r"^https://(?P<host>github\.com|gitlab\.com|bitbucket\.org)/(?P<repo>[^/]+/[^/#?]+?)(?:\.git)?"
    r"(?:(?:/-)?/(?:tree|blob|src)/(?P<ref>[^/]+)(?:/(?P<path>[^?#]*?))?)?/?(?:[?#].*)?$")
ROOT_NAMES = ("index.md", "README.md", "index.rst", "README.rst", "index.html")
DOC_DIRS = ("docs", "doc", "documentation", "docs/source", "doc/source", "source")


def is_remote(source: str) -> bool:
    return "://" in source or source.startswith("git@")


def write_nav(out: Path, nav: list) -> None:
    (out / "mkdocs.yml").write_text(
        "# Written by skilltree fetch: the docs hierarchy, for `map`.\n"
        + yaml.safe_dump({"docs_dir": "docs", "nav": nav}, sort_keys=False, allow_unicode=True))


def nav_item(title: str, path: str | None, children: list) -> dict:
    """A mkdocs nav entry: a page, or a section holding its page and children."""
    if not children:
        return {title: path}
    return {title: ([{title: path}] if path else []) + children}


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def fetch(source: str, out: Path, ref: str | None = None, path: str | None = None,
          refresh: bool = False, max_pages: int = 500) -> dict:
    """Make the docs available as markdown; return {"root": <root .md>, ...}."""
    work = out / "fetch"
    cache = work / "fetch.json"
    key = {"source": source, "ref": ref, "path": path}
    if cache.is_file() and not refresh and is_remote(source):  # local files may change
        cached = json.loads(cache.read_text())
        if cached.get("key") == key and Path(cached["result"]["root"]).is_file():
            return cached["result"] | {"cached": True}
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    out = work

    if not is_remote(source):
        base = Path(source).expanduser().resolve()
        result = from_local(base / path if path else base, out, {"kind": "local"})
    elif source.startswith("git@") or source.endswith(".git") or GIT_URL_RE.match(source):
        result = from_git(source, out, ref, path)
    else:
        result = from_website(source, out, max_pages)
    warnings = result.pop("warnings", [])
    if warnings:
        (out / "fetch-warnings.txt").write_text("\n".join(warnings) + "\n")
        result["warnings"] = f"{len(warnings)} (see {out / 'fetch-warnings.txt'})"
    cache.write_text(json.dumps({"key": key, "result": result}, indent=2) + "\n")
    return result


def from_local(base: Path, out: Path, info: dict) -> dict:
    """Find the root doc under base; convert rst/html trees to markdown."""
    root = find_root(base)
    if root.suffix == ".rst":
        return info | convert_sphinx(root, out)
    if root.suffix in (".html", ".htm"):
        pages = {p.resolve().as_uri(): p.read_text(encoding="utf-8", errors="replace")
                 for p in root.parent.rglob("*.htm*")}
        site = HtmlSite(root.resolve().as_uri(), out, max_pages=len(pages) + 1, pages=pages,
                        root=root.parent.resolve().as_uri() + "/")
        return info | site.convert()
    return info | {"root": str(root)}


def find_root(base: Path) -> Path:
    """The root doc of a docs tree: the file itself, the mkdocs/Sphinx index, or a usual name."""
    if base.is_file():
        return base
    if not base.is_dir():
        raise Error(f"docs not found: {base}")
    for name in ("mkdocs.yml", "mkdocs.yaml"):
        if (cfg := base / name).is_file():
            conf = yaml.load(cfg.read_text(encoding="utf-8"), Loader=MkdocsLoader) or {}
            docs_dir = base / conf.get("docs_dir", "docs")
            for index in ("index.md", "README.md"):
                if (docs_dir / index).is_file():
                    return docs_dir / index
    for d in ("", *DOC_DIRS):  # Sphinx: its master doc, .rst or MyST .md
        if (base / d / "conf.py").is_file():
            master = sphinx_conf(base / d)["master"]
            for ext in (".rst", ".md"):
                if (base / d / (master + ext)).is_file():
                    return base / d / (master + ext)
    for d in ("", *DOC_DIRS):
        for name in ROOT_NAMES:
            if (base / d / name).is_file():
                return base / d / name
    raise Error(f"no root doc in {base} (looked for mkdocs.yml, Sphinx conf.py and "
                f"{', '.join(ROOT_NAMES)}); pass the root file or --path")


# --------------------------------------------------------------------------
# git: shallow, sparse checkout of the docs folder
# --------------------------------------------------------------------------

def git(*args: str, cwd: Path | None = None) -> str:
    try:
        return subprocess.run(["git", *args], cwd=cwd, check=True, text=True,
                              capture_output=True).stdout
    except FileNotFoundError:
        raise Error("git not found on PATH")
    except subprocess.CalledProcessError as exc:
        raise Error(f"git {' '.join(args)} failed: {exc.stderr.strip()}")


def git_checkout(url: str, ref: str | None, path: str | None, dest: Path) -> None:
    """Fetch one commit without blobs, then check out only the folder holding the docs."""
    dest.mkdir(parents=True)
    git("init", "-q", cwd=dest)
    git("remote", "add", "origin", url, cwd=dest)
    try:
        git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", ref or "HEAD", cwd=dest)
    except Error:  # server without partial clone support
        git("fetch", "-q", "--depth", "1", "origin", ref or "HEAD", cwd=dest)
    sparse = None
    if path:
        kind = git("ls-tree", "FETCH_HEAD", path.rstrip("/"), cwd=dest).split()
        if not kind:
            raise Error(f"{path} not found in {url}{' at ' + ref if ref else ''}")
        sparse = path.rstrip("/") if kind[1] == "tree" else posixpath.dirname(path)
    else:
        top = git("ls-tree", "--name-only", "-d", "FETCH_HEAD", cwd=dest).split()
        sparse = next((d for d in ("docs", "doc", "documentation") if d in top), None)
    if sparse:  # cone mode: that folder plus the files at the repo root
        git("sparse-checkout", "set", sparse, cwd=dest)
    git("checkout", "-q", "FETCH_HEAD", cwd=dest)


def from_git(source: str, out: Path, ref: str | None, path: str | None) -> dict:
    url = source
    if m := GIT_URL_RE.match(source):
        url = f"https://{m['host']}/{m['repo']}.git"
        ref, path = ref or m["ref"], path or m["path"] or None
    dest = out / "source"
    git_checkout(url, ref, path, dest)
    return from_local(dest / path if path else dest, out,
                      {"kind": "git", "source": url, "ref": ref or "default branch"})


# --------------------------------------------------------------------------
# reStructuredText (Sphinx) -> markdown
# --------------------------------------------------------------------------

PUNCT_LINE = re.compile(r"^([=\-`:'\"~^_*+#<>.])\1+\s*$")
LABEL_RE = re.compile(r"^\.\. _([^:\n]+):\s*$")
ROLE_RE = re.compile(r":(?:std:)?(doc|ref|numref|any):`([^`]+)`")
TARGET_RE = re.compile(r"^(.*?)\s*<([^<>]+)>$", re.S)
INCLUDE_RE = re.compile(r"^(\s*\.\. include::\s*)(\S.*?)\s*$", re.M)


def sphinx_conf(srcdir: Path) -> dict:
    """The few conf.py settings needed, read with regexes (conf.py is never run)."""
    text = (srcdir / "conf.py").read_text(encoding="utf-8") if (srcdir / "conf.py").is_file() else ""
    master = re.search(r"^(?:master_doc|root_doc)\s*=\s*['\"]([^'\"]+)", text, re.M)
    excl = re.search(r"^exclude_patterns\s*=\s*\[(.*?)\]", text, re.M | re.S)
    prolog = re.search(r"^rst_prolog\s*=\s*[rRuU]?(\"\"\"|''')(.*?)\1", text, re.M | re.S)
    epilog = re.search(r"^rst_epilog\s*=\s*[rRuU]?(\"\"\"|''')(.*?)\1", text, re.M | re.S)
    return {"master": master[1] if master else "index",
            "exclude": re.findall(r"['\"]([^'\"]+)['\"]", excl[1]) if excl else [],
            "prolog": prolog[2] if prolog else "", "epilog": epilog[2] if epilog else ""}


def section_title(lines: list[str], start: int = 0) -> str | None:
    """The first section title at or after line `start` (text line + underline)."""
    for i in range(start, len(lines) - 1):
        text = lines[i].strip()
        if text and not PUNCT_LINE.match(lines[i]) and PUNCT_LINE.match(lines[i + 1]) \
                and len(lines[i + 1].strip()) >= len(text):
            return text
    return None


def parse_toctrees(lines: list[str]) -> list[dict]:
    """Every `.. toctree::`, also inside grid tables: entries, options and line span."""
    found = []
    for i, line in enumerate(lines):
        for hit in re.finditer(r"\.\. toctree::", line):  # a table row may hold several
            found.append(parse_toctree(lines, i, hit.start(), line.lstrip().startswith("|")))
    return found


def parse_toctree(lines: list[str], i: int, col: int, in_table: bool) -> dict:
    entries, opts, end = [], {}, i
    for j in range(i + 1, len(lines)):
        nxt = lines[j]
        if in_table:
            if nxt.lstrip().startswith("+"):
                break
            cell = nxt[col:].split("|")[0]
        else:
            if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= col:
                break
            cell = nxt[col:]
        end = j
        if text := cell.strip():
            if m := re.match(r"^:([\w-]+):\s*(.*)$", text):
                opts[m[1]] = m[2]
            else:
                entries.append(text)
    return {"entries": entries, "opts": opts, "start": i, "end": end,
            "col": col, "in_table": in_table}


class SphinxProject:
    def __init__(self, root: Path, out: Path):
        srcdir = next((d for d in (root.parent, *root.parent.parents)
                       if (d / "conf.py").is_file()), root.parent)
        self.src, self.out, self.conf = srcdir, out / "docs", sphinx_conf(srcdir)
        self.root = root.relative_to(srcdir).with_suffix("").as_posix()
        self.docs = {}
        for p in sorted(srcdir.rglob("*.rst")):
            rel = p.relative_to(srcdir)
            if any(part.startswith(("_", ".")) for part in rel.parts) or \
                    any(fnmatch.fnmatch(rel.as_posix(), pat) for pat in self.conf["exclude"]):
                continue
            self.docs[rel.with_suffix("").as_posix()] = p.read_text(encoding="utf-8", errors="replace")
        self.docs.setdefault(self.root, root.read_text(encoding="utf-8", errors="replace"))
        self.lines = {d: t.splitlines() for d, t in self.docs.items()}
        self.titles = {d: section_title(ls) or posixpath.basename(d) for d, ls in self.lines.items()}
        self.labels = {}
        for d, ls in self.lines.items():
            for i, line in enumerate(ls):
                if m := LABEL_RE.match(line):
                    self.labels[m[1].strip().lower()] = (d, section_title(ls, i + 1))
        self.toctrees = {d: parse_toctrees(ls) for d, ls in self.lines.items()}

    def resolve(self, current: str, target: str) -> str | None:
        """A toctree / :doc: target as a docname, relative to the current doc."""
        target = re.sub(r"\.(rst|txt)$", "", target.strip())
        name = target[1:] if target.startswith("/") else \
            posixpath.normpath(posixpath.join(posixpath.dirname(current), target))
        return name if name in self.docs else None

    def link(self, current: str, docname: str) -> str:
        return posixpath.relpath(docname + ".md", posixpath.dirname(current) or ".")

    def entries(self, current: str, tree: dict) -> list[tuple[str, str]]:
        """(title, docname) for each toctree entry, globs expanded."""
        result = []
        for entry in tree["entries"]:
            m = TARGET_RE.match(entry)
            title, target = (m[1], m[2]) if m else (None, entry)
            if target == "self" or "://" in target:
                continue
            if "glob" in tree["opts"] and any(c in target for c in "*?["):
                pattern = posixpath.normpath(posixpath.join(posixpath.dirname(current), target))
                result += [(self.titles[d], d) for d in sorted(self.docs) if fnmatch.fnmatch(d, pattern)]
            elif d := self.resolve(current, target):
                result.append((title or self.titles[d], d))
        return result

    def preprocess(self, d: str) -> str:
        """Sphinx-only syntax pandoc does not know: toctrees, :doc:, :ref:, prolog."""
        lines = list(self.lines[d])
        for tree in reversed(self.toctrees[d]):
            if tree["in_table"]:
                continue
            pad = " " * tree["col"]
            items = [f"{pad}* `{t.replace('<', '').replace('`', '')} <{self.link(d, doc)}>`__"
                     for t, doc in self.entries(d, tree)]
            lines[tree["start"]:tree["end"] + 1] = items + [""]
        text = "\n".join(lines)

        def role(m: re.Match) -> str:
            kind, body = m[1], m[2]
            t = TARGET_RE.match(body)
            text_, target = (t[1], t[2]) if t else (None, body)
            if kind == "doc" and (doc := self.resolve(d, target)):
                return f"`{text_ or self.titles[doc]} <{self.link(d, doc)}>`__"
            if hit := self.labels.get(target.strip().lower()):
                return f"`{text_ or hit[1] or target} <{self.link(d, hit[0])}>`__"
            return f"*{text_ or target}*"

        text = ROLE_RE.sub(lambda m: role(m).replace("\n", " "), text)
        text = f"{self.conf['prolog']}\n\n{text}\n\n{self.conf['epilog']}\n"

        def include(m: re.Match) -> str:  # absolute = from the Sphinx source dir
            target = m[2]
            if target.startswith("<"):
                return ""  # docutils' standard includes (<isonum.txt>, ...)
            path = self.src / target[1:] if target.startswith("/") else None
            return m[1] + str(path) if path else m[0]

        return INCLUDE_RE.sub(include, text)

    def convert_one(self, d: str) -> str | None:
        src = self.src / (d + ".rst")
        dest = self.out / (d + ".md")
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            md = pandoc(self.preprocess(d), "rst", cwd=src.parent)
        except Error as exc:
            dest.write_text(self.docs[d])  # keep the raw text: still readable
            return f"{d}.rst: kept as rst ({exc})"
        md = re.sub(r"\[\\\|([^\]]+?)\\\|\]\(##SUBST##[^)]*\)", r"|\1|", md)  # undefined subs
        if not md.lstrip().startswith("# "):
            md = f"# {self.titles[d]}\n\n{md}"
        dest.write_text(md)
        return None

    def nav(self, d: str, seen: set) -> list:
        seen.add(d)
        items, section = [], None
        for tree in self.toctrees[d]:
            entries = [nav_item(t, doc + ".md", self.nav(doc, seen))
                       for t, doc in self.entries(d, tree) if doc not in seen and not seen.add(doc)]
            if caption := tree["opts"].get("caption"):
                items.append({caption: entries})
            else:
                items += entries
        return items


def convert_sphinx(root: Path, out: Path) -> dict:
    proj = SphinxProject(root, out)
    with ThreadPoolExecutor(8) as pool:
        warnings = [w for w in pool.map(proj.convert_one, sorted(proj.docs)) if w]
    nav = proj.nav(proj.root, set())
    if nav:
        write_nav(out, nav)
    return {"format": "sphinx rst", "docs": str(proj.out), "pages": len(proj.docs),
            "root": str(proj.out / (proj.root + ".md")), "warnings": warnings}


def pandoc(text: str, fmt: str, cwd: Path | None = None) -> str:
    import pypandoc  # bundles pandoc (pypandoc_binary); imported only when needed

    cmd = [pypandoc.get_pandoc_path(), "-f", fmt, "-t", "gfm", "--wrap=none"]
    res = subprocess.run(cmd, input=text, cwd=cwd, capture_output=True, text=True)
    if res.returncode:
        raise Error(f"pandoc: {res.stderr.strip()[:300]}")
    # Leftover wrappers from unknown directives / layout divs carry no content.
    return re.sub(r"(?m)^[ \t]*</?div\b[^>]*>[ \t]*\n?", "", res.stdout)


# --------------------------------------------------------------------------
# HTML sites (a website, or locally built HTML) -> markdown
# --------------------------------------------------------------------------

MAIN_SELECTORS = ("[role=main]", "article", "main", ".md-content", ".rst-content",
                  "#content", ".document", ".body", "body")
JUNK_SELECTORS = ("script", "style", "noscript", "nav", "footer", "form", "button", "svg",
                  "a.headerlink", ".headerlink", ".copybutton", ".content-icon-container",
                  ".edit-this-page", ".view-this-page", ".related-pages", ".bottom-of-page",
                  ".toc-drawer", ".md-source-file", ".rst-footer-buttons", ".prev-next-area",
                  ".sphx-glr-download", "[role=navigation]", ".breadcrumbs", ".wy-breadcrumbs")
SKIP_PAGES = re.compile(r"(^|/)(_static|_sources|_images|_downloads|_modules|genindex|search|"
                        r"py-modindex|objects\.inv|404)(/|\.|$)")


def http_get(url: str) -> tuple[str, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            ctype = resp.headers.get("Content-Type", "")
            final = resp.geturl()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise Error(f"GET {url}: {exc}")
    charset = re.search(r"charset=([\w-]+)", ctype)
    return data.decode(charset[1] if charset else "utf-8", errors="replace"), final, ctype


def common_dir(urls: list[str]) -> str:
    """The deepest folder URL holding all the given page URLs."""
    parts = [u.rsplit("/", 1)[0].split("/") for u in urls]
    common = []
    for segs in zip(*parts):
        if len(set(segs)) > 1:
            break
        common.append(segs[0])
    return "/".join(common) + "/"


def page_key(url: str) -> str:
    """A page URL without query or fragment; directory URLs end in index.html."""
    url = urllib.parse.urldefrag(url)[0].split("?")[0]
    return url + "index.html" if url.endswith("/") else url


class HtmlSite:
    """Pages of one docs site, converted to markdown under <out>/docs/."""

    def __init__(self, start: str, out: Path, max_pages: int, pages: dict | None = None,
                 root: str | None = None):
        self.start, self.out, self.max_pages = page_key(start), out, max_pages
        self.pages = {page_key(u): t for u, t in (pages or {}).items()}  # key -> html
        self.offline = pages is not None
        self.base = self.start.rsplit("/", 1)[0] + "/"  # crawl scope without a nav
        # Pages the nav may link to: the given root, else the whole host.
        self.site_root = root or "/".join(self.start.split("/", 3)[:3]) + "/"
        self.warnings: list[str] = []

    def in_site(self, url: str, scope: str | None = None) -> bool:
        key = page_key(url)
        if not key.startswith(scope or self.site_root) or SKIP_PAGES.search(key):
            return False
        last = key.rsplit("/", 1)[1]
        return last.endswith((".html", ".htm")) or "." not in last

    def get(self, key: str) -> str | None:
        if key not in self.pages:
            if self.offline:
                return None
            try:
                html, final, ctype = http_get(key)
            except Error as exc:
                self.warnings.append(str(exc))
                self.pages[key] = None
                return None
            self.pages[key] = html if "html" in ctype else None
            if page_key(final) != key and "html" in ctype:
                self.pages.setdefault(page_key(final), html)
        return self.pages[key]

    def get_many(self, keys: list[str]) -> None:
        todo = [k for k in dict.fromkeys(keys) if k not in self.pages]
        with ThreadPoolExecutor(4) as pool:  # polite: a few requests at a time
            list(pool.map(self.get, todo))

    # -- hierarchy ---------------------------------------------------------

    def sidebar(self, soup, url: str) -> list[dict]:
        """The site's navigation tree: Sphinx toctree sidebar, else the biggest nav list."""
        from bs4 import Tag

        def owner(el):
            return el.find_parent("li")

        def node(li) -> dict | None:
            a = next((x for x in li.find_all("a", href=True) if owner(x) is li), None)
            ul = next((x for x in li.find_all("ul") if owner(x) is li), None)
            kids = [n for c in (ul.find_all("li", recursive=False) if ul else []) if (n := node(c))]
            href = urllib.parse.urljoin(url, a["href"]) if a else None
            page = page_key(href) if href and "#" not in a["href"] and self.in_site(href) else None
            label = a or next((x for x in li.find_all(["label", "span", "p"]) if owner(x) is li), li)
            title = " ".join(label.get_text(" ", strip=True).split())
            return {"title": title, "url": page, "children": kids} if (page or kids) and title else None

        l1 = soup.select("li.toctree-l1")
        if l1:  # Sphinx: every theme marks the global toctree like this
            groups, nodes = {}, []
            for li in l1:
                ul = li.parent
                if id(ul) not in groups:
                    cap = ul.find_previous_sibling(class_="caption")
                    groups[id(ul)] = {"title": cap.get_text(" ", strip=True), "url": None,
                                      "children": []} if cap else None
                    if groups[id(ul)]:
                        nodes.append(groups[id(ul)])
                if n := node(li):
                    (groups[id(ul)]["children"] if groups[id(ul)] else nodes).append(n)
            return nodes
        main = self.main(soup)
        best, score = None, 2
        for el in soup.find_all(["nav", "div", "aside"]):
            if not isinstance(el, Tag) or (main and (el is main or main in el.parents or el in main.parents)):
                continue
            ul = el.find("ul")
            n = sum(1 for a in el.find_all("a", href=True)
                    if self.in_site(urllib.parse.urljoin(url, a["href"])))
            if ul and n > score:
                best, score = ul, n
        if not best:
            return []
        return [n for li in best.find_all("li", recursive=False) if (n := node(li))]

    def subtree(self, nodes: list[dict]) -> list[dict]:
        """If the start page is a section deeper in the nav, keep only that section."""
        def find(ns, depth=0):
            for i, n in enumerate(ns):
                if n["url"] == self.start:
                    return n, depth, i
                if hit := find(n["children"], depth + 1):
                    return hit
            return None
        hit = find(nodes)
        if hit and hit[0]["children"] and (hit[1] > 0 or hit[2] > 0):
            return hit[0]["children"]
        return nodes

    # -- conversion --------------------------------------------------------

    @staticmethod
    def main(soup):
        return next((el for sel in MAIN_SELECTORS if (el := soup.select_one(sel))), None)

    def md_path(self, key: str) -> str:
        rel = key[len(self.site_root):]
        rel = re.sub(r"\.html?$", "", rel) if rel.endswith((".html", ".htm")) else rel + "/index"
        return urllib.parse.unquote(rel) + ".md"

    def convert_page(self, key: str) -> None:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(self.pages[key], "html.parser")
        main = self.main(soup) or soup
        for sel in JUNK_SELECTORS:
            for el in main.select(sel):
                el.decompose()
        for div in main.select("div[class*=highlight-]"):  # Sphinx code blocks
            lang = next((c[10:] for c in div["class"] if c.startswith("highlight-")), "")
            pre = div.find("pre")
            if pre:
                new = soup.new_tag("pre")
                code = soup.new_tag("code", attrs={"class": f"language-{lang}"}
                                    if lang not in ("", "default", "none", "text") else {})
                code.string = pre.get_text()
                new.append(code)
                div.replace_with(new)
        here = self.md_path(key)
        for a in main.find_all("a", href=True):
            href = urllib.parse.urljoin(key, a["href"])
            target, frag = urllib.parse.urldefrag(href)
            if page_key(target) == key and frag:
                a["href"] = "#" + frag
            elif page_key(target) in self.converted:
                rel = posixpath.relpath(self.md_path(page_key(target)), posixpath.dirname(here) or ".")
                a["href"] = rel + ("#" + frag if frag else "")
            else:
                a["href"] = href
        for img in main.find_all("img", src=True):
            img["src"] = urllib.parse.urljoin(key, img["src"])
        keep = {"href", "src", "alt", "title", "colspan", "rowspan"}
        for el in main.find_all(True):  # attributes markdown can't hold force raw HTML
            el.attrs = {k: v for k, v in el.attrs.items()
                        if k in keep or (k == "class" and el.name == "code")}
        try:
            md = pandoc(str(main), "html-native_divs-native_spans")
        except Error as exc:
            self.warnings.append(f"{key}: {exc}")
            return
        dest = self.out / "docs" / here
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(md)

    def convert(self) -> dict:
        from bs4 import BeautifulSoup

        if self.get(self.start) is None:
            raise Error(f"could not read {self.start}")
        soup = BeautifulSoup(self.pages[self.start], "html.parser")
        nav = self.subtree(self.sidebar(soup, self.start))
        urls = []

        def collect(ns):
            for n in ns:
                if n["url"]:
                    urls.append(n["url"])
                collect(n["children"])
        collect(nav)
        if self.offline:  # local files: the nav may list pages that are not there
            urls = [u for u in urls if self.pages.get(u)]
        if urls:  # crawl just what the nav lists (plus the start page)
            keys = [self.start] + urls[: self.max_pages - 1]
            self.get_many(keys)
        else:  # no nav: breadth-first over links below the start page's folder
            keys, queue = [self.start], [self.start]
            while queue and len(keys) < self.max_pages:
                html = self.get(queue.pop(0))
                if not html:
                    continue
                found = [page_key(urllib.parse.urljoin(keys[0], a["href"]))
                         for a in BeautifulSoup(html, "html.parser").find_all("a", href=True)]
                new = [k for k in dict.fromkeys(found)
                       if k not in keys and self.in_site(k, scope=self.base)]
                new = new[: self.max_pages - len(keys)]
                keys += new
                self.get_many(new)
                queue += new
        keys = [k for k in dict.fromkeys(keys) if self.pages.get(k)]
        # Paths are relative to the deepest folder holding every page.
        self.site_root = common_dir(keys)
        self.converted = set(keys)
        with ThreadPoolExecutor(8) as pool:
            list(pool.map(self.convert_page, keys))

        def to_nav(ns):
            items = []
            for n in ns:
                path = self.md_path(n["url"]) if n["url"] in self.converted else None
                kids = to_nav(n["children"])
                if path or kids:
                    items.append(nav_item(n["title"], path, kids))
            return items
        if nav and (items := to_nav(nav)):
            write_nav(self.out, items)
        root = self.out / "docs" / self.md_path(self.start)
        return {"format": "html", "docs": str(self.out / "docs"), "pages": len(keys),
                "root": str(root), "warnings": self.warnings}


def from_website(url: str, out: Path, max_pages: int) -> dict:
    html, final, ctype = http_get(url)
    if "html" not in ctype:  # e.g. a raw .md or .rst file served over HTTP
        raise Error(f"{final} is {ctype or 'not HTML'}: pass a docs page, a git URL or a local path")
    site = HtmlSite(final, out, max_pages)
    site.pages[page_key(final)] = html
    return {"kind": "website", "source": final} | site.convert()
