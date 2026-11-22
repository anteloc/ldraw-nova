---
name: iskillz
license: AGPL-3.0
description: >
  Turn API docs (markdown, e.g. a mkdocs site, from a git repo or a local
  folder) into an installable tree of agent skills: a root SKILL.md with the
  API's core concepts and linked subskills for each task, so agents load only
  the part of the API a task needs. Use when the user wants to make a skill
  from API documentation or install a generated skill tree. Also use when
  working in a project that needs a library, SDK or API you have no skill for
  and whose docs are large or unfamiliar (the user names it, or the code
  starts depending on it): fetch its docs, build its skill tree and install it
  into that project.
---

# iskillz: API docs → skill tree

Large API docsets bloat an agent's context and mix concerns. This skill
turns a docs tree into a **skill tree** that agents navigate like a person
navigates the docs: start at the root, open only the subskill for the task.

Run the script with Python 3.11+ (`python` instead of `python3` on
Windows). Nothing to install first: on its first run it installs its own
dependencies into a private virtualenv (`~/.cache/iskillz/venv`, about a
minute), then reuses it:

```bash
python3 <skill-dir>/scripts/skilltree.py <command> ...
```

`<skill-dir>` is this skill's directory (the one holding this file). The
script runs from any directory: relative paths are relative to where you run
it.

## From another project: an API skill on demand

Use this when you are working in some project (not this skill's repo) and
the task needs an API that has no skill yet.

1. **Trigger.** Either the user asked for it ("make a skill for X", "learn
   the X API"), or you found the need yourself: the task depends on a
   library or API whose docs are big or that you don't know well. If you
   found it yourself, tell the user in one line what you're about to build
   and ask before starting: it runs an agent for a few minutes and writes into
   the project.
2. **Skip if it exists.** Look in the project's skill directories
   (`.claude/skills/`, `.agents/skills/`, ...) and your personal ones for a
   skill with that API's name. If one is there, use it instead.
3. **Find the docs source**, from the package metadata (`pyproject.toml`,
   `package.json`, `Cargo.toml` repository/documentation URLs), its
   homepage, or a web search. Any of these works (see [Fetch](#0-fetch)):
   - **Markdown docs in a repo** (`docs/`, `mkdocs.yml`): pass the
     GitHub/GitLab URL of the folder or root file
     (`.../tree/<ref>/docs`, `.../blob/<ref>/docs/index.md`).
   - **A docs website** (Sphinx, mkdocs, ...): pass the URL of its first
     page, e.g. `https://mujoco.readthedocs.io/en/stable/overview.html`.
     Prefer it over the repo for Sphinx projects: the built pages hold what
     Sphinx extensions generate (API signatures, autodoc), which the `.rst`
     sources lack.
   - **reStructuredText in a repo**, when no site is published: pass the
     root `.rst`, e.g.
     `https://github.com/google-deepmind/mujoco/blob/main/doc/index.rst`.

   Pick the version the project uses: a tag (`--ref v1.2.3`, or in the
   URL) for a repo, the matching version path (`/en/1.2.3/`) for a site.
4. **Build and install.** Keep the workspace out of the project
   (`~/.cache/iskillz/<api>`), and install into the project:

   ```bash
   python3 <skill-dir>/scripts/skilltree.py build <source> \
       -o ~/.cache/iskillz/<api> --project <project-dir>
   ```

   **You** do the planning and writing: run it without `--agent`. It does
   the mechanical steps, then stops at the first step that needs judgment
   and prints `pending:` prompt files. For each one, read it, do what it
   says, and write the answer to the path at its end. Then run the same
   `build` command again. It goes plan → skills → check → install, stopping
   twice (once for the plan, once for the skill bodies), and is done when it
   prints `installed:`. The skill prompts are independent: if you can run
   subagents, give each one a prompt file and its answer path, in parallel.
   Show the user `taxonomy.md` and `plan.md` (mermaid diagrams) on the way.

   `--project` installs into `<project-dir>/<agent-dir>/skills/` for each
   agent config directory the project has (`.claude`, `.agents`, `.qwen`,
   `.codex`, `.gemini`, `.opencode`). If it has none, use
   `--to <project-dir>/.claude/skills` (or your agent's equivalent).
5. **Use it.** The new skill is in the project now, but agents usually
   load skills only at session start. Read its root `SKILL.md` and follow
   the links to the subskill your task needs, then carry on with the
   original task. Tell the user it was installed (and that they can commit
   it, so the whole team gets it).

If `build` stops with problems, the workspace keeps every step's output:
fix it by hand or with the single steps below, then `check` and `install`.

## Pipeline

Every step reads and writes files in a workspace (`-o/--out`, default
`build/`), so you can stop, review or hand-edit between steps.

| Step | Command | Writes | Who |
| --- | --- | --- | --- |
| 0. Fetch | `fetch <source>` | `source/` (git only), root doc path | script |
| 1. Map | `map <root.md>` | `taxonomy.json`, `taxonomy.md` | script |
| 2. Plan | `plan` | `plan.json`, `plan.md` | you (or `--agent`) |
| 3. Generate | `generate` | `<skill-name>/**/SKILL.md` | you (or `--agent`) |
| 4. Check | `check <out>/<skill-name>` | report | script |
| 5. Package | `package <out>/<skill-name>` | `<skill-name>.zip` | script |
| 6. Install | `install <dir-or-zip> --to <skills-dir> \| --project <dir>` | skill copy | script |

`build <source> [--to <skills-dir> | --project <dir>]` runs 0-4 (and 6) in
one go.

```bash
python3 <skill-dir>/scripts/skilltree.py fetch https://github.com/org/lib/tree/main/docs -o work
python3 <skill-dir>/scripts/skilltree.py map <root printed by fetch> -o work
python3 <skill-dir>/scripts/skilltree.py plan -o work
python3 <skill-dir>/scripts/skilltree.py generate -o work
python3 <skill-dir>/scripts/skilltree.py check work/<skill-name>
python3 <skill-dir>/scripts/skilltree.py package work/<skill-name>  # -> work/<skill-name>.zip
python3 <skill-dir>/scripts/skilltree.py install work/<skill-name>.zip --to ~/.claude/skills
```

All commands accept `--json`, and exit non-zero on failure.

### 0. Fetch

Gets the docs as markdown and prints the `root` doc to pass to `map`. All
of it goes in `<out>/fetch/`: a remote source is reused on later runs unless
`--refresh`. The source can be:

| Source | Example | What happens |
| --- | --- | --- |
| local file or folder | `docs/`, `docs/index.md`, `_build/html/` | used in place (markdown), or converted (`.rst`, `.html`) |
| git repo | `https://github.com/org/lib`, `git@...`, `....git` | shallow clone of just the docs folder (`docs/`, `doc/`) |
| GitHub/GitLab folder or file | `.../tree/<ref>/docs`, `.../blob/<ref>/doc/index.rst` | same, for that branch/tag and path |
| docs website | `https://lib.readthedocs.io/en/stable/overview.html` | downloads the pages listed in the site's sidebar nav (or, without one, those linked below the start page's folder, up to `--max-pages`, default 500) |

`--ref` picks a branch or tag, `--path` a folder or file inside the source.
In a folder, the root doc is the mkdocs index (from `mkdocs.yml`), the
Sphinx master doc (from `conf.py`), else `index.md`, `README.md`,
`index.rst` or `index.html`, also under `docs/` or `doc/`.

Markdown is used as it is. reStructuredText and HTML are converted with
pandoc (bundled, nothing to install) into `<out>/fetch/docs/`, and their
hierarchy goes into `<out>/fetch/mkdocs.yml` as a nav, so `map` keeps it:
Sphinx `toctree`s for `.rst` (with `:ref:`/`:doc:` turned into links and the
`rst_prolog` applied), the sidebar's table of contents for a website. Pages
that could not be read or converted are listed in
`<out>/fetch/fetch-warnings.txt`.

### 1. Map

Crawls the docs from the root doc. If a `mkdocs.yml` with a `nav:` sits above
the root, its nav is the hierarchy (the authors' own). Otherwise the script
follows local `.md` links breadth-first. Show the user `taxonomy.md` (a
mermaid diagram) before planning.

### 2. Plan

You (or the `--agent`) group the docs into a skill tree following
[references/planning.md](references/planning.md); the prompt is
`<out>/prompts/plan.md`, the answer `<out>/answers/plan.json`: root = core concepts, one
subskill per task, reference pages in their own branch, non-usage pages
(license, support, ...) left out. Review `plan.md` with the user. Edit
`plan.json` by hand when needed: `generate` re-validates it.

### 3. Generate

You (or the `--agent`, `-j` in parallel, default 4) write each node's body
following [references/writing.md](references/writing.md), from that node's
source docs: one prompt per node in `<out>/prompts/<skill>/.../<node>.md`,
answers in `<out>/answers/` at the same paths.
The script adds the frontmatter, a linked **Subskills** list, and verbatim
copies of the source docs under `references/`. Rewrite single nodes with
`--only <name> ...`. Saved answers are reused on later runs: `--redo` asks
again (writes fresh prompts, or re-asks the `--agent`). To regenerate from
scratch, delete `<out>/<skill-name>` and `<out>/answers/` first (`generate`
does not remove skills that left the plan).

### 4. Check

Runs the official [`skills-ref`](https://agentskills.io) validator on every
SKILL.md, then checks local links, the 500-line limit, and that every
subskill is linked from its parent. Fix problems with `generate --only` or by
editing the file.

### 5. Package

Checks the tree (as in step 4), then zips it into a single installer with
one top-level `<skill-name>/` folder (`-o` sets the zip path). That is the
layout skill upload forms expect, and what `install` accepts, so share the
zip instead of a folder.

### 6. Install

Only when the user asks, or as the last step of the on-demand workflow
above. Installs a skill directory or a `package` zip into a skills directory
(`--to`, default `~/.agents/skills`; Claude Code uses `~/.claude/skills`), or
with `--project <dir>` into each agent's skills directory in that project.
Refuses to overwrite unless `--force`.

## Who does the judgment steps

Plan and generate need an agent, and by default it is **you**, the agent
using this skill: without `--agent`, those steps write prompt files and wait
for your answers (see step 4 of the on-demand workflow). Do not pass
`--agent` yourself: it hands the work to another agent.

`--agent "<command>"` is for people running the pipeline by hand on the
command line: the script pipes each prompt to that command on stdin and saves
what it prints as the answer, e.g. `--agent "claude -p"`. There is no default,
so whoever runs it chooses, and knows, which agent writes the skill.

## Output layout

```
<out>/
├── taxonomy.json / taxonomy.md   docs tree (+ mermaid)
├── plan.json / plan.md           skill tree (+ mermaid)
├── prompts/ , answers/           judgment tasks and their answers (plan.json, <skill>/**.md)
└── <api-name>/                   the skill to install
    ├── SKILL.md                  core concepts + Subskills list
    ├── references/               verbatim source docs
    └── <task>/SKILL.md           subskill, same shape, nested
```

Subskills are plain SKILL.md files in subdirectories, linked from their
parent. Agents discover only the root skill and follow the links on demand.

Worked example: [examples/moonshine/](https://github.com/anteloc/iskillz/tree/master/examples/moonshine) (Moonshine Voice).

## Adding tools

See [references/adding-tools.md](references/adding-tools.md).
