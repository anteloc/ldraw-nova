# Baseline repair log

Start UTC: 2026-10-26 15:41:45. Infrastructure pause estimated from last completed tool at 15:46:30 to resume at 20:26:19: 16,789 seconds, excluded from active trial time. Approximate active deadline: 20:51:34 UTC.

Initial discovery: three CLI syntax/registry failures (`part --geometry`, multi-ID `technic parts`, uncurated 40490). These are not review-to-source repair cycles. The curated 32278 rail was selected without changing the registry. Initial vertical-shaft concept was rejected before authoring after inspecting the actual 64179 hole axes.

Failed review-to-source-correction cycles: 1 (visual review). Automatic review/checks passed on revision 1, but image/source inspection identified that the hand knob had no outside axial stop. Revision 2 moves the complete chain plane inward 10 LDU (wheel spacing/radii unchanged), centres both 12L shafts at X=0, uses right half-bush bearing stops and adds a half bush outside the hand knob. No check was relaxed.

Additional tool limitation: direct ldraw-render-steps.sh reported only three steps for a four-group section without a trailing STEP. Used the documented manual prepare fallback; no toolkit edits.

Second infrastructure pause: last completed timed command ended 2026-10-26 20:31:59.023756 UTC; resumption was 2026-10-27 05:54:14 UTC. Estimated pause 33,734.976244 seconds, excluded. Active periods before this resumption total 625.023756 seconds.

The first attempt to refresh the separately named MPD returned exit 2 because the output already existed. This was a CLI output-protection event, not a source defect. Rebuilt with the documented `--force` after validation; the final named MPD is byte-identical to the reviewed model. Refreshed the frame manual from that final MPD and opened every page.

Final counts: 1 failed visual-review-to-source-correction cycle; 0 failed automatic-review-to-source-correction cycles; 0 external expert interventions; no toolkit, dependency, shipped example, library or validator changes. Read-only searches/report reads, image-tool calls, metadata writing and reasoning were not timed by the command wrapper; active wall time includes them.
