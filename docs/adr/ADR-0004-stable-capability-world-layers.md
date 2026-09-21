# ADR-0004: Three-layer knowledge separation

## Context

Frontier docs blur stable rules, vendor capabilities, and world facts inside prompts.

## Decision

Enforce GOS-I25 layers:

1. **Stable Core** — constitution, authority/epistemic semantics  
2. **Capability Registry** — models/tools/prices/limits (volatile)  
3. **World Facts** — observations about the external world  

EnvironmentCompiler selects capabilities by **properties**, never by product marketing names.

## Also decided

- ReasoningBudget ≠ VerificationRequirement (GOS-I23)  
- Execution trace is evidence candidate only (GOS-I22)  
- Judge cannot self-validate (GOS-I24)  
- No constitutional κ≥0.75 or “80% environment / 20% prompt” as fact  

## Reversal trigger

Only if a formal open standard encodes all three layers without prompt conflation.
