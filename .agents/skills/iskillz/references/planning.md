# Planning a skill tree from a docs taxonomy

You turn a docs taxonomy (a tree of doc pages with their titles, headings and
sizes) into a **skill tree**: one root skill for the API, with subskills that
an agent opens only when its task needs them. Think of how a developer finds
their way through the docs to get one job done, and lay out that path.

## Rules

1. **Root = the API.** Name it after the API (e.g. `moonshine-voice`). Its
   sources are the pages with the core concepts every task needs: overview,
   quickstart, installation, the main usage pattern.
2. **One subskill per task or feature area**, named by what an agent is asked
   to do (`transcription`, `text-to-speech`, `voice-agent`), not by the page
   title. Mirror the docs' hierarchy where it already groups things by task;
   regroup where it does not.
3. **Sources are whole docs**, given by their `path` in the taxonomy. Merge
   small related pages into one skill. A doc may feed several skills when
   several tasks depend on it (e.g. an options reference).
4. **Reference pages** (API reference, option lists, C API) go under a
   reference subskill with one child per large page, so a task skill can
   point to them instead of repeating them.
5. **Leave out** pages that do not help anyone use the API: license,
   acknowledgements, support/community links, release process, contributor
   notes, marketing comparisons. Benchmarks and papers stay only if they
   help pick between options (e.g. which model size), merged into that skill.
6. **Shape:** at most 3 levels below the root; 2-9 children per node; no
   skill with a single child (merge it into its parent).
7. **name:** lowercase letters, digits and single hyphens, max 64 characters,
   unique among siblings. It becomes the directory name.
8. **description:** max 1024 characters, third person. Say what the skill
   covers **and when to use it** ("Use when ..."), and name the key classes,
   functions, CLI commands or options an agent would see in a request or in
   code, so the agent can match a task to the skill from the description alone.

## Output

Your answer is **only** a JSON object, no prose and no code fence, in this shape
(`children` nodes have the same shape, recursively):

{
  "name": "api-name",
  "description": "What it covers. Use when ...",
  "sources": ["index.md", "quickstart.md"],
  "children": [
    {
      "name": "task-name",
      "description": "What it covers. Use when ...",
      "sources": ["using/task.md"],
      "children": []
    }
  ]
}
