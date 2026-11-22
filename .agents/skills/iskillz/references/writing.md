# Writing one skill of a skill tree

You write the body of one SKILL.md in a skill tree generated from API docs.
An agent reads it when its task matches the skill's description, so it must
get that agent from "I need to do X" to working code.

## Output

Your answer is **only** the markdown body:

- No YAML frontmatter, and no code fence around the whole answer.
- Do **not** write a subskills list or a source docs list: both are appended
  automatically after your text, with links.
- Start with `# <Title>` and a short paragraph saying what this skill lets
  the agent do.

## Content

- **Root skill:** the mental model and the concepts every subskill relies on:
  what the API is, how to install it, the canonical usage pattern, shared
  conventions (naming across languages, error handling, lifecycle). End with
  a short "which subskill for which task" guide if the descriptions alone
  are not enough.
- **Task skill:** task-oriented. Steps, a minimal working example, the
  options and parameters that matter, common pitfalls and errors.
- **Reference skill:** a compact, scannable summary (tables, signatures).
  Point to the verbatim copy for the long tail instead of trying to fit
  everything.
- Do not repeat what the parent skills cover; refer to it in one line.

## Accuracy

- Use **only** facts from the source docs. Never invent class, function,
  parameter or option names, defaults or behaviour.
- Copy code examples and signatures **verbatim** (you may trim lines that
  do not matter to the task).
- When the docs show the same example in several languages, keep them all
  if short; otherwise keep the primary language in full and state how the
  others differ (e.g. `on_text` → `onText`).
- If the docs are unclear or incomplete on a point, say so rather than guess.

## Links

- Rewrite links between docs into links to the skill that holds that doc,
  using the relative paths in your assignment (drop `#anchors`).
- Keep external `https://` links. Drop images and links to docs that are
  not in the tree.

## Style

- Under 300 lines; 500 is a hard limit. Lead with what is needed most often.
- Imperative voice, short sentences, tables for option lists.
