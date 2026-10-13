# Cognitive organs — contracts locked

**Status:** `CONTRACTS_LOCKED` — see `organs/`  
**Zone:** T2 cognition / eval missions — **not** new T0 Authority surfaces (ADR-0009)

Reliability organs (G1–Gfull) remain substrate. These organs are Intelligence/Execution.

| Organ | Contract | Stub |
|-------|----------|------|
| Decomposer | `organs/DECOMPOSER.md` | `cognition.organs.decomposer` |
| Pivot/Replan | `organs/PIVOT_REPLAN.md` | `cognition.organs.pivot_replan` |
| Orchestration | `organs/ORCHESTRATION.md` | `cognition.organs.orchestration` |

Each contract includes: I/O · Authority · Quality · Errors · **Control-transfer** · Tests.

## Build order (next)

```text
1. Organ contracts LOCKED (this pack)
2. Lock CHALLENGE-GA-v1 terminal goal + stop conditions (concrete target)
3. Deepen organ impl behind contracts (still no Authority bypass)
4. Execute Challenge; score terminal Goal — not intermediate plans alone
```

No organ may bypass Authority Kernel or invent PRODUCTION_PROVEN.
