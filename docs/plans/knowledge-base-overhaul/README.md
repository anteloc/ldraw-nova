# Knowledge-base overhaul

Planning baseline preserved on 2026-11-03 before implementation.

- [Target structure](snapshot/target-structure.md)
- [Documentation migration ledger](snapshot/document-migration-ledger.md)
- [Example migration ledger](snapshot/example-migration-ledger.md)
- [Catalog/export compatibility and implementation order](snapshot/catalog-export-migration.md)
- [Visual findings and audit coverage](snapshot/README.md)
- [Snapshot identity](snapshot-manifest.json)
- [Implementation record](implementation.md)
- [Implementation preservation checks](implementation-checks.json)
- [Export/build/BOM checks](export-checks.json)
- [Manual review identity reconciliation](manual-history-audit.json)

Keep the snapshot immutable. Record actual changes, checks and deviations in the implementation record. The original planning and visual evidence remain in `output/kb-visual-audit/`; large rendered images are local evidence rather than duplicated in this snapshot. Snapshot scripts preserve the original inventory method; they target the original audit directory and are not migration commands.
