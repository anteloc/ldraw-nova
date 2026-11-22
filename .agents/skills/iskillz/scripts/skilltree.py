#!/usr/bin/env python3
"""Turn a tree of API docs into a tree of agent skills.

Pipeline. Every step reads and writes files in the --out workspace, so you can
stop, inspect or hand-edit between steps:

  fetch SOURCE  get the docs as markdown (local, git, Read the Docs, website)
                -> fetch/ with the root doc (see docsource.py)
  map ROOT.md   crawl the docs        -> taxonomy.json, taxonomy.md (mermaid)
  plan          agent groups docs     -> plan.json, plan.md (mermaid)
  generate      agent writes nodes    -> <skill-name>/**/SKILL.md
  check DIR     validate a skill tree (skills-ref + links)
  package DIR   zip a skill into an installer (DIR.zip)
  install SRC   install a skill (directory or .zip) into a skills directory
                or into a project's agent skill directories (--project)
  build SOURCE  fetch + map + plan + generate + check (+ install)

The judgment steps (plan, generate) need an agent. By default that is the
agent running this script: the step writes each task as a prompt file under
<out>/prompts/ (saying where the answer goes, in <out>/answers/), stops, and
lists what is pending; the agent writes the answers and runs the same command
again. On the command line, pass --agent "<command>" (e.g. --agent "claude -p")
to have the script pipe each prompt to that agent and save its answers itself.
Answers are reused on later runs (--redo asks again). The agent instructions
are references/planning.md and references/writing.md either way.
"""

import argparse
import itertools
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ inside installed skills (often committed)

import bootstrap  # noqa: E402

bootstrap.ensure()  # plain Python: installs the dependencies below on first run

import yaml  # noqa: E402
from markdown_it import MarkdownIt  # noqa: E402
from skills_ref import validate  # noqa: E402

from docsource import Error, MkdocsLoader, fetch as fetch_docs  # noqa: E402

REFS = Path(__file__).resolve().parent.parent / "references"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_LINES = 500  # Agent Skills guidance for a SKILL.md body

# Indented code blocks are off so content nested in mkdocs tabs
# (`=== "Python"` + 4-space indent) is still parsed as markdown.
MD = MarkdownIt("commonmark").disable("code")


# --------------------------------------------------------------------------
# Markdown helpers
# --------------------------------------------------------------------------

def parse_md(text: str) -> tuple[list[str], list[str]]:
    """Return the h1-h3 headings and the link targets of a markdown text."""
    tokens = MD.parse(text)
    headings, links = [], []
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open" and tok.tag in ("h1", "h2", "h3"):
            headings.append("#" * int(tok.tag[1]) + " " + tokens[i + 1].content)
        links += [c.attrs["href"] for c in tok.children or [] if c.type == "link_open"]
    return headings, links


def is_local(href: str) -> bool:
    return "://" not in href and not href.startswith(("mailto:", "#"))


def mermaid(tree: dict, label) -> str:
    """Render a {..., "children": [...]} tree as a mermaid flowchart."""
    ids = itertools.count()
    lines = ["```mermaid", "graph LR"]

    def walk(node, parent=None):
        nid = f"n{next(ids)}"
        text = label(node).replace('"', "#quot;")
        lines.append(f'  {nid}["{text}"]')
        if parent:
            lines.append(f"  {parent} --> {nid}")
        for child in node.get("children", []):
            walk(child, nid)

    walk(tree)
    return "\n".join(lines + ["```"])


# --------------------------------------------------------------------------
# fetch: get the docs as markdown (see docsource.py)
# --------------------------------------------------------------------------

def cmd_fetch(args) -> dict:
    return fetch_docs(args.source, Path(args.out), ref=args.ref, path=args.path,
                      refresh=args.refresh, max_pages=args.max_pages)


# --------------------------------------------------------------------------
# map: crawl docs into a taxonomy tree
# --------------------------------------------------------------------------

def doc_node(docs_dir: Path, rel: str, title: str | None = None) -> dict:
    text = (docs_dir / rel).read_text(encoding="utf-8")
    headings, links = parse_md(text)
    h1 = next((h[2:] for h in headings if h.startswith("# ")), Path(rel).stem)
    return {"title": title or h1, "path": rel, "lines": len(text.splitlines()),
            "headings": headings, "links": links, "children": []}


def nav_nodes(items: list, docs_dir: Path, skip: str) -> list[dict]:
    """Turn a mkdocs `nav:` list into taxonomy nodes (sections have path None)."""
    nodes = []
    for item in items:
        title, value = next(iter(item.items())) if isinstance(item, dict) else (None, item)
        if isinstance(value, list):
            nodes.append({"title": title, "path": None,
                          "children": nav_nodes(value, docs_dir, skip)})
        elif value != skip and is_local(value):
            node = doc_node(docs_dir, value, title)
            del node["links"]
            nodes.append(node)
    return nodes


def crawl_links(docs_dir: Path, root_rel: str) -> dict:
    """Breadth-first walk of local .md links; a doc's parent is where it was first linked."""
    tree = doc_node(docs_dir, root_rel)
    queue, seen = [tree], {root_rel}
    while queue:
        node = queue.pop(0)
        for href in node.pop("links"):
            target = (docs_dir / node["path"]).parent / href.split("#")[0]
            if not is_local(href) or target.suffix != ".md" or not target.is_file():
                continue
            rel = os.path.relpath(target, docs_dir)
            if rel.startswith("..") or rel in seen:
                continue
            seen.add(rel)
            child = doc_node(docs_dir, rel)
            node["children"].append(child)
            queue.append(child)
    return tree


def find_mkdocs(root: Path) -> Path | None:
    for d in root.parents:
        for name in ("mkdocs.yml", "mkdocs.yaml"):
            if (d / name).is_file():
                return d / name
    return None


def build_taxonomy(root: Path) -> dict:
    """Prefer the mkdocs nav (the authors' own hierarchy); fall back to links."""
    if not root.is_file():
        raise Error(f"root doc not found: {root}")
    cfg = find_mkdocs(root)
    if cfg:
        conf = yaml.load(cfg.read_text(encoding="utf-8"), Loader=MkdocsLoader) or {}
        docs_dir = (cfg.parent / conf.get("docs_dir", "docs")).resolve()
        if conf.get("nav") and docs_dir in root.parents:
            rel = root.relative_to(docs_dir).as_posix()
            tree = doc_node(docs_dir, rel)
            del tree["links"]
            tree["children"] = nav_nodes(conf["nav"], docs_dir, skip=rel)
            return {"docs_dir": docs_dir, "source": f"mkdocs nav ({cfg.name})", "tree": tree}
    docs_dir = root.parent
    return {"docs_dir": docs_dir, "source": "markdown links",
            "tree": crawl_links(docs_dir, root.name)}


def cmd_map(args) -> dict:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    taxonomy = build_taxonomy(Path(args.root).resolve())
    # Stored relative to the workspace so it can be moved or committed.
    taxonomy["docs_dir"] = os.path.relpath(taxonomy["docs_dir"], out.resolve())
    (out / "taxonomy.json").write_text(json.dumps(taxonomy, indent=2) + "\n")
    diagram = mermaid(taxonomy["tree"], lambda n: n["title"] + (
        f"<br/><small>{n['path']} · {n['lines']} lines</small>" if n["path"] else ""))
    (out / "taxonomy.md").write_text(
        f"# Docs taxonomy\n\nSource: {taxonomy['source']}\n\n{diagram}\n")
    return {"taxonomy": str(out / "taxonomy.json"), "diagram": str(out / "taxonomy.md")}


# --------------------------------------------------------------------------
# Agent plumbing
# --------------------------------------------------------------------------

def ask(agent: str, prompt: str) -> str:
    """Send a prompt to a CLI agent on stdin; return its stdout."""
    try:
        result = subprocess.run(shlex.split(agent), input=prompt,
                                capture_output=True, text=True)
    except FileNotFoundError:
        raise Error(f"agent command not found: {agent!r} (set --agent)")
    if result.returncode:
        raise Error(f"agent exited {result.returncode}: {result.stderr.strip()[-800:]}")
    return result.stdout.strip()


def answer(out: Path, rel: str, prompt: str, what: str, agent: str | None,
           redo: bool) -> str | None:
    """The answer to a prompt: saved, from --agent, or None after writing the prompt.

    rel names the task (e.g. "plan.json", "<skill>/<sub>.md"): its answer lives
    in <out>/answers/<rel>, its prompt in <out>/prompts/<rel without suffix>.md.
    """
    ans = out / "answers" / rel
    if ans.is_file() and not redo:
        return ans.read_text(encoding="utf-8")
    ans.parent.mkdir(parents=True, exist_ok=True)
    if agent:
        text = ask(agent, prompt)
        ans.write_text(text + "\n", encoding="utf-8")
        return text
    ans.unlink(missing_ok=True)
    prompt_file = out / "prompts" / Path(rel).with_suffix(".md")
    prompt_file.parent.mkdir(parents=True, exist_ok=True)
    prompt_file.write_text(prompt + f"""

# Where your answer goes

Write {what}, and nothing else, to this file:

    {ans.resolve()}
""", encoding="utf-8")
    return None


def pending_note(cmd: str) -> str:
    return (f"read each pending prompt, write its answer where it says, then run `{cmd}` "
            "again (prompts are independent: hand them to subagents in parallel if you can)")


def unfence(text: str) -> str:
    """Drop a code fence wrapping the whole answer, which agents sometimes add."""
    m = re.fullmatch(r"```[\w-]*\n(.*)\n```", text.strip(), re.DOTALL)
    return m.group(1) if m else text


def walk(node: dict, parent: Path = Path(), ancestors: tuple = ()):
    """Yield (node, dir relative to the workspace, ancestor nodes) depth-first."""
    here = parent / node["name"]
    yield node, here, ancestors
    for child in node.get("children", []):
        yield from walk(child, here, ancestors + (node,))


# --------------------------------------------------------------------------
# plan: agent groups docs into a skill tree
# --------------------------------------------------------------------------

def load_plan(out: Path) -> dict:
    """Read plan.json, resolving docs_dir (stored relative to the workspace)."""
    plan_file = out / "plan.json"
    if not plan_file.is_file():
        raise Error(f"{plan_file} not found: run `plan` first")
    plan = json.loads(plan_file.read_text())
    plan["docs_dir"] = str((out / plan["docs_dir"]).resolve())
    return plan


def plan_problems(plan: dict) -> list[str]:
    docs_dir = Path(plan["docs_dir"])
    problems = []
    for node, here, _ in walk(plan["skill"]):
        name = node.get("name", "")
        if not NAME_RE.match(name) or len(name) > 64:
            problems.append(f"{here}: bad name {name!r} (lowercase-hyphen, max 64)")
        if not 0 < len(node.get("description", "")) <= 1024:
            problems.append(f"{here}: description must be 1-1024 characters")
        names = [c.get("name") for c in node.get("children", [])]
        problems += [f"{here}: duplicate child {n!r}" for n in set(names) if names.count(n) > 1]
        problems += [f"{here}: source not found: {s}" for s in node.get("sources", [])
                     if not (docs_dir / s).is_file()]
    return problems


def cmd_plan(args) -> dict:
    out = Path(args.out)
    taxonomy_file = out / "taxonomy.json"
    if not taxonomy_file.is_file():
        raise Error(f"{taxonomy_file} not found: run `map` first")
    taxonomy = json.loads(taxonomy_file.read_text())
    prompt = "\n\n".join([
        (REFS / "planning.md").read_text(),
        "# Taxonomy to plan from",
        "```json\n" + json.dumps(taxonomy["tree"], indent=1) + "\n```",
    ])
    text = answer(out, "plan.json", prompt, "the JSON object of the skill tree",
                  args.agent, args.redo)
    if text is None:
        return {"pending": [str(out / "prompts" / "plan.md")], "next": pending_note("plan")}
    try:
        skill = json.loads(text[text.find("{"):text.rfind("}") + 1])
    except json.JSONDecodeError as exc:
        raise Error(f"the plan answer ({out / 'answers' / 'plan.json'}) is not a JSON "
                    f"object ({exc}); fix or delete it:\n{text[:800]}")
    plan = {"docs_dir": taxonomy["docs_dir"], "skill": skill}
    (out / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    diagram = mermaid(skill, lambda n: f"<b>{n['name']}</b>" + (
        "<br/><small>" + "<br/>".join(n["sources"]) + "</small>" if n.get("sources") else ""))
    (out / "plan.md").write_text(f"# Skill tree plan\n\n{diagram}\n")
    return {"plan": str(out / "plan.json"), "diagram": str(out / "plan.md"),
            "problems": plan_problems(load_plan(out))}


# --------------------------------------------------------------------------
# generate: agent writes each SKILL.md
# --------------------------------------------------------------------------

def node_prompt(node: dict, here: Path, ancestors: tuple, plan: dict) -> str:
    docs_dir = Path(plan["docs_dir"])
    lines = [(REFS / "writing.md").read_text(), "# Your assignment", "",
             f"Write the body of the `{node['name']}` skill.", "",
             f"Description: {node['description']}", ""]
    if ancestors:
        lines += ["Parent skills (already cover their own topics, do not repeat them):"]
        lines += [f"- {a['name']}: {a['description']}" for a in ancestors]
        lines.append("")
    if node.get("children"):
        lines += ["Subskills (listed automatically after your text):"]
        lines += [f"- {c['name']}: {c['description']}" for c in node["children"]]
        lines.append("")
    lines += ["Where each doc lives in the skill tree (use these paths to rewrite links):"]
    for other, other_dir, _ in walk(plan["skill"]):
        target = os.path.relpath(other_dir / "SKILL.md", here)
        lines += [f"- {src} -> {target}" for src in other.get("sources", [])]
    lines += ["", "# Source docs", ""]
    for src in node.get("sources", []):
        text = (docs_dir / src).read_text(encoding="utf-8")
        lines += [f'<doc path="{src}">', text, "</doc>", ""]
    return "\n".join(lines)


def ref_name(src: str) -> str:
    return src.replace("/", "-")


def render(node: dict, body: str) -> str:
    front = yaml.safe_dump({"name": node["name"], "description": node["description"]},
                           sort_keys=False, allow_unicode=True, width=10**6)
    parts = [f"---\n{front}---", body.strip()]
    if node.get("children"):
        parts.append("## Subskills\n\nRead the one that matches your task:\n\n" + "\n".join(
            f"- [{c['name']}]({c['name']}/SKILL.md): {c['description']}"
            for c in node["children"]))
    if node.get("sources"):
        parts.append("## Source docs\n\nVerbatim copies, for details not covered above:\n\n"
                     + "\n".join(f"- [{s}](references/{ref_name(s)})" for s in node["sources"]))
    return "\n\n".join(parts) + "\n"


def write_node(node, here: Path, plan: dict, out: Path, body: str) -> None:
    node_dir = out / here
    (node_dir / "references").mkdir(parents=True, exist_ok=True)
    for src in node.get("sources", []):
        shutil.copyfile(Path(plan["docs_dir"]) / src, node_dir / "references" / ref_name(src))
    (node_dir / "SKILL.md").write_text(render(node, unfence(body)))


def cmd_generate(args) -> dict:
    out = Path(args.out)
    plan = load_plan(out)
    if problems := plan_problems(plan):
        return {"problems": problems}
    nodes = [n for n in walk(plan["skill"]) if not args.only or n[0]["name"] in args.only]

    redo = args.redo or bool(args.only)

    def job(item):
        node, here, ancestors = item
        try:
            body = answer(out, f"{here}.md", node_prompt(node, here, ancestors, plan),
                          "the markdown body of this skill", args.agent, redo)
        except Error as exc:
            return "problem", f"{here}: {exc}"
        if body is None:
            return "pending", str(out / "prompts" / f"{here}.md")
        write_node(node, here, plan, out, body)
        print(f"wrote {here}/SKILL.md", file=sys.stderr)
        return "written", str(here)

    with ThreadPoolExecutor(args.jobs if args.agent else 1) as pool:
        results = list(pool.map(job, nodes))
    result = {"skill": str(out / plan["skill"]["name"]),
              "written": sum(1 for kind, _ in results if kind == "written"),
              "problems": [v for kind, v in results if kind == "problem"]}
    if pending := [v for kind, v in results if kind == "pending"]:
        result |= {"pending": pending, "next": pending_note("generate")}
    return result


# --------------------------------------------------------------------------
# check / install
# --------------------------------------------------------------------------

def check_tree(root: Path) -> list[str]:
    if not (root / "SKILL.md").is_file():
        return [f"{root}: no SKILL.md"]
    problems = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        d = skill_md.parent
        problems += [f"{d}: {e}" for e in validate(d.resolve())]
        text = skill_md.read_text(encoding="utf-8")
        if (n := len(text.splitlines())) > MAX_LINES:
            problems.append(f"{skill_md}: {n} lines (keep under {MAX_LINES})")
        for href in parse_md(text)[1]:
            target = href.split("#")[0]
            if is_local(href) and target and not (d / target).exists():
                problems.append(f"{skill_md}: broken link {href}")
        parent_md = d.parent / "SKILL.md"
        if d != root and (not parent_md.is_file()
                          or f"{d.name}/SKILL.md" not in parent_md.read_text(encoding="utf-8")):
            problems.append(f"{skill_md}: not linked from {parent_md}")
    return problems


def cmd_check(args) -> dict:
    root = Path(args.dir)
    return {"skill": str(root), "skills": len(list(root.rglob("SKILL.md"))),
            "problems": check_tree(root)}


def cmd_package(args) -> dict:
    """Zip a skill as <name>/... (the layout skill uploaders and `install` expect)."""
    src = Path(args.dir).resolve()
    if problems := check_tree(src):
        return {"problems": problems}
    base = Path(args.output).with_suffix("") if args.output else src.parent / src.name
    archive = shutil.make_archive(str(base), "zip", root_dir=src.parent, base_dir=src.name)
    return {"package": archive}


def zip_skill_name(path: Path) -> str:
    """Name of the single top-level skill directory in a skill zip."""
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
    tops = {n.split("/")[0] for n in names}
    if len(tops) != 1 or f"{next(iter(tops))}/SKILL.md" not in names:
        raise Error(f"{path} is not a skill package (expected one <name>/SKILL.md)")
    return tops.pop()


# Project-local skill directories, by the agent config directory that holds them.
AGENT_DIRS = (".claude", ".agents", ".qwen", ".codex", ".gemini", ".opencode")


def project_skill_dirs(project: Path) -> list[Path]:
    """<project>/<agent-dir>/skills for every agent config directory in the project."""
    if not project.is_dir():
        raise Error(f"project not found: {project}")
    dirs = [project / d / "skills" for d in AGENT_DIRS if (project / d).is_dir()]
    if not dirs:
        raise Error(f"no agent directory ({', '.join(AGENT_DIRS)}) in {project}; "
                    "pass --to <project>/<agent-dir>/skills instead")
    return dirs


def install_one(src: Path, to: Path, force: bool) -> str:
    is_zip = src.suffix == ".zip"
    dest = to / (zip_skill_name(src) if is_zip else src.name)
    if dest.exists():
        if not force:
            raise Error(f"{dest} exists (use --force to replace it)")
        shutil.rmtree(dest)
    to.mkdir(parents=True, exist_ok=True)
    if is_zip:
        shutil.unpack_archive(src, to)  # zipfile drops absolute and ".." paths
    else:
        shutil.copytree(src, dest)
    return str(dest)


def cmd_install(args) -> dict:
    src = Path(args.dir).resolve()
    if src.suffix != ".zip" and not (src / "SKILL.md").is_file():
        raise Error(f"{src} is not a skill (no SKILL.md) nor a .zip package")
    if args.project and args.to:
        raise Error("pass --to or --project, not both")
    if args.project:
        targets = project_skill_dirs(Path(args.project).expanduser().resolve())
    else:
        targets = [Path(args.to or "~/.agents/skills").expanduser()]
    return {"installed": [install_one(src, to, args.force) for to in targets]}


def cmd_build(args) -> dict:
    result = cmd_fetch(args)
    args.root = result["root"]
    result |= cmd_map(args)
    for step in (cmd_plan, cmd_generate):
        result |= step(args)
        if result.get("problems") or result.get("pending"):
            if result.get("pending"):
                result["next"] = pending_note("build")  # re-run the whole command
            return result
    args.dir = result["skill"]
    result |= cmd_check(args)
    if (args.to or args.project) and not result["problems"]:
        result |= cmd_install(args)
    return result


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main() -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="emit JSON")
    workspace = argparse.ArgumentParser(add_help=False)
    workspace.add_argument("-o", "--out", default="build",
                           help="workspace directory (default: build)")
    agent = argparse.ArgumentParser(add_help=False)
    agent.add_argument("--agent", metavar="COMMAND",
                       help='agent command that reads a prompt on stdin and prints the answer, '
                       'e.g. "claude -p" (default: none, write prompts for the calling agent)')
    agent.add_argument("--redo", action="store_true",
                       help="ignore saved answers and ask again")
    agent.add_argument("-j", "--jobs", type=int, default=4,
                       help="with --agent: skills written in parallel (default: 4)")

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(required=True, metavar="command")

    source = argparse.ArgumentParser(add_help=False)
    source.add_argument("source", help="docs: a root .md/.rst/.html file or docs folder, a git "
                        "URL (GitHub/GitLab .../tree|blob/<ref>/<path> too), or a docs web page "
                        "(Read the Docs or any site)")
    source.add_argument("--ref", help="git branch or tag (default: the repo's default branch)")
    source.add_argument("--path", help="docs directory or root .md inside the source")
    source.add_argument("--refresh", action="store_true", help="fetch again instead of reusing <out>/fetch")
    source.add_argument("--max-pages", type=int, default=500,
                        help="most pages to download from a website (default: 500)")
    target = argparse.ArgumentParser(add_help=False)
    target.add_argument("--to", help="skills directory (default: ~/.agents/skills)")
    target.add_argument("--project", metavar="DIR", help="install into DIR/<agent-dir>/skills "
                        f"for each agent directory found ({', '.join(AGENT_DIRS)})")
    target.add_argument("--force", action="store_true", help="replace an existing install")

    p = sub.add_parser("fetch", parents=[common, workspace, source],
                       help="get the docs and find the root doc")
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser("map", parents=[common, workspace], help="crawl docs into a taxonomy")
    p.add_argument("root", help="root markdown doc, e.g. docs/index.md")
    p.set_defaults(func=cmd_map)

    p = sub.add_parser("plan", parents=[common, workspace, agent], help="agent plans the skill tree")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("generate", parents=[common, workspace, agent], help="agent writes the skills")
    p.add_argument("--only", nargs="+", metavar="NAME", help="(re)write only these skills")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("check", parents=[common], help="validate a skill tree")
    p.add_argument("dir", help="skill directory (the one holding the root SKILL.md)")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("package", parents=[common], help="zip a skill into an installer")
    p.add_argument("dir", help="skill directory")
    p.add_argument("-o", "--output", help="zip path (default: <dir>.zip)")
    p.set_defaults(func=cmd_package)

    p = sub.add_parser("install", parents=[common, target], help="install a skill (directory or .zip)")
    p.add_argument("dir", metavar="src", help="skill directory or .zip from `package`")
    p.set_defaults(func=cmd_install)

    p = sub.add_parser("build", parents=[common, workspace, agent, source, target],
                       help="fetch + map + plan + generate + check (+ install with --to/--project)")
    p.set_defaults(func=cmd_build, only=None)

    args = parser.parse_args()
    try:
        result = args.func(args)
    except Error as exc:
        print(f"skilltree: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            if key == "problems":
                continue
            if isinstance(value, list):
                print(f"{key}:" + "".join(f"\n  {v}" for v in value))
            else:
                print(f"{key}: {value}")
        for problem in result.get("problems", []):
            print(f"problem: {problem}", file=sys.stderr)
    return 1 if result.get("problems") else 0


if __name__ == "__main__":
    sys.exit(main())
