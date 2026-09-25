# R3 OPEN_HYPOTHESES (executor)

| H | Statement | Decision |
|---|-----------|----------|
| H-A1 | process_log SHA mismatches file hash ⇒ tampering | **REJECTED** — dir merkle matches; semantics issue |
| H-A2 | Sealed packs leaked into git | **REJECTED** — gitignored; on-disk scorer-local |
| H-A3 | R1 already had independent review | **REJECTED** — R2 first |
| H-A4 | Y22 freeze SHAs missing from Tasktracker | **REJECTED** |
| H-A5 | Tests regenerate frozen mission artifacts | **SUPPORTED** (HIGH) |
| H-B1 | unique_key duplicates in sample | measured |
| H-B-agency | agency mostly missing | **REJECTED** |
| H-B-burst | same-timestamp bursts exist | sample-relative CONFIRMED/WEAK |
