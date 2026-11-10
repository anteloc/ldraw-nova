# Construction examples

Search by the role needed for the new brief, then open the returned package README:

```sh
./ldraw-agent knowledge search 'sideways panel attachment'
./ldraw-agent examples 'mounted hoses'
./ldraw-agent knowledge show technic:service-platform
```

Each semantic package owns its lesson, editable source, interfaces, provenance and scoped evidence. Subject and technique are independent. Small fittings share packages; section observations stay attached to their actual parent.

[Plan basics](plan-basics/README.md) and [flex basics](flex-basics/README.md) teach syntax and tooling. [Boombox](boombox/README.md) teaches a particular panel construction; choose it for that lesson, not as a default silhouette. Aircraft lessons are indexed by the [aircraft atlas](aircraft-atlas/README.md) and the [aircraft guide](../docs/agent/guides/aircraft.md).

The `*-atlas` directories retain compatibility indexes and historical preparation inputs while migration is completed. [Archived identities](archive/README.md), diagnostic fixtures, inspiration and held sources are opt-in. See the [retrieval contract](../docs/agent/reference/cli.md#retrieve-construction-knowledge) and [migration record](../docs/plans/knowledge-base-overhaul/implementation.md).
