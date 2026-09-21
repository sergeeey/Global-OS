# ORGANIZATION_MODEL.md

## Principle

$$
Goal \rightarrow Organization \rightarrow Execution
$$

Not: Goal → fixed agents / personas.

## Organizational Unit

Fields: id, mission, parent/children, inputs, output_contract, authority, budget, state, deadline, required_independence, escalation, artifact_namespace.

## Organizational Compiler (inputs → OrganizationGraph)

Goal Contract, task dependency graph, risk, expertise, parallelizability, verification needs, budget, deadline, authority, information locality.

## Topologies

single_solver · pipeline · manager_workers · recursive_hierarchy · parallel_exploration · independent_ensemble · committee · blackboard · specialist_cells · verification_branch · hybrid

## Span of control

Dynamic: maximize Value − CoordinationCost − ComputeCost − ErrorRisk.  
v0: heuristics.

## Leader contract

Decomposition, assignment, allocation, monitoring, conflict resolution, integration, escalation — **not** epistemic authority.

## Artifact-first communication

Workers write artifacts/evidence/structured results to shared store.  
Leaders pass references — no summary-of-summary chains as sole channel.

## Ephemeral workers

Created for a task; destroyed after. Persist artifacts, events, evidence, decisions, cost, performance — not personas.

## Verification Plane

Organizationally independent of claim authors.  
VerificationRouter selects protocol by result class and tier.
