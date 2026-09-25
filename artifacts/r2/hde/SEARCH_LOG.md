# R2-HDE search log (non-exhaustive)

## Channels attempted
- Exact/semantic web search (agent scaffolding nulls, Agentless, Reflexion, CCI, checklists, GAIA)
- Campaign artifact read (Y20–Y22, R1)
- Citation follow from search hits to arXiv/NEJM/GitHub

## Queries (sample)
1. LLM agent scaffolding vs baseline null result
2. ReAct Reflexion ablation no improvement
3. Agentless SWE-bench outperforms agents
4. AI agent evaluation intervention cost reproducibility
5. WHO surgical checklist effect limitations
6. GAIA benchmark human assistance
7. model capability vs scaffolding ablation
8. CoT does not improve negative result (tool error — partial)

## Branch coverage
- H+: checklists; Reflexion gains on some tasks; R1 keep; richer GOS traces
- H−: Agentless; DirectSolve; CCI; Reflexion WebShop failure; WebShop repro collapse
- H0: Y20–Y22 ties/nulls; scaffolding ablations flat/negative on cheap models
- Halt: model capacity; fixed pipeline; Hawthorne; contamination

## Failures
- Some WebSearch calls errored (timeout/tool); not retried exhaustively
- Full text of some meta-analyses paywalled; used abstracts/PMC excerpts
