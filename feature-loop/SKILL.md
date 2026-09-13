---
name: feature-loop
description: Carry a feature through all remaining stages, filling missing plans, delegating independent stages to subagents, reviewing and integrating results, and checking the original intent throughout. Use for an autonomous feature loop or coordinated parallel delivery; discussion, planning, review, or one stage alone retains its requested scope.
---

# Feature Loop

Own delivery of the requested feature across its stages. Act as coordinator:
maintain the contract and delivery map, dispatch bounded work, evaluate results,
and integrate verified changes. Continue after each stage without asking whether
to proceed. User decisions and authorization persist across the loop.

This skill coordinates work within the available session. It does not schedule
future sessions or restart a terminated process. Preserve a checkpoint for a
later invocation when interrupted or stopped by the host.

## Establish the run

1. Read repository instructions, the user's intent, existing brief/specification,
   stage map, and relevant code. Inspect the branch, worktrees, diff, and existing
   PRs before allocating work. Preserve unrelated changes and resume existing work.
2. Identify the finish line: all requested behavior demonstrated, affected
   integrations checked, and review findings resolved or explicitly accepted.
   Separate code readiness, environment verification, and user acceptance.
3. Use the available `feature-*` skills when their work is needed. Resolve them
   from the installed skill catalog; do not assume sibling installation paths.
   Load each once, when needed. If unavailable, perform that bounded phase
   directly using the contracts below and disclose any missing review capability.
4. Read [coordination.md](references/coordination.md) before recording the run or
   dispatching workers. Keep the existing specification as the shared contract;
   the coordinator alone updates it and the execution checkpoint.

Starting the loop authorizes implementation and ordinary fixes across the
requested stages. It does not add permission to publish, merge into shared
branches, deploy, or change the product scope. Reuse permissions already granted;
ask only at an actual unresolved boundary after preparing the available work.

## Maintain intent and plan

- Use `feature-shape` to resolve missing direction or an assumption overturned by
  evidence. Keep the accepted goal, exclusions, and guarantees as the reference.
  Use `feature-plan` to create or update the specification and stage breakdown.
- Map every accepted requirement to a stage and its verification. Fill missing
  coverage, including failure handling and integration. Add stages only for the
  agreed scope; record optional ideas in the existing Later section.
- Detail the next ready stages, normally one to three, as capacity becomes
  available. Keep later stages as outlines. Preserve stage IDs when revising the
  map; when splitting, redirect dependencies to the parts that satisfy them.
- A missing stage document is planning work to do, not a reason to wait for the
  user. A missing product decision blocks only the work that depends on it.
- Check alignment before dispatch and after each integrated result: does the
  change preserve the intended behavior, assumptions, boundaries, and necessary
  guarantees? Does the remaining map still cover the goal? Revisit full shaping
  only when new evidence changes the direction.
- Classify new findings as an implementation defect, a plan/coverage gap, a
  missing intent decision, or an unrelated improvement. Fix the first two within
  the accepted contract. Bring a concrete recommendation for material changes
  to behavior, shared guarantees, or scope. Do not weaken requirements to fit code.
- If a contract changes, assess affected active and completed stages. Stop or
  redirect affected workers, invalidate stale evidence, and update their briefs.
  Unaffected work may continue. A changed contract must not silently validate an
  implementation reviewed against the old one. Apply the durable invalidation
  transition in [coordination.md](references/coordination.md) before scheduling.

## Dispatch ready work

Keep at most two stages active by default, including stages awaiting review or
integration. Adapt to explicit user limits and the host's available agent slots;
reserve capacity for a reviewer. Workers do not create further subagents.

Run the read-only [loop_state.py](scripts/loop_state.py) helper on the checkpoint
to check the graph and propose a compatible set of pending stages. Its selection
is advisory: confirm actual prerequisites, write scope, shared interfaces, and
environment availability before dispatch. Different files alone do not establish
independence. Declare shared mutable resources such as a test database or port.

When subagents are available, delegate implementation to a worker using
`feature-step`, with one stage active per worker. Give it the packet in
[coordination.md](references/coordination.md), including its assigned workspace.
The worker returns its result to the coordinator instead of advancing the parent
plan, creating a PR, or choosing another stage.

For parallel writes, create a separate branch and worktree per stage from a
known integration commit. Create worktrees sequentially and pass their absolute
paths explicitly; spawning a subagent does not itself isolate files or Git state.
Separate test resources too. If isolation is unavailable, run writes sequentially
in the designated workspace. With no subagent tools, implement sequentially and
record independent review as pending rather than calling self-review independent.

Use one integration branch for the feature unless an existing workflow or user
instruction requires another strategy. In this loop, dependent stages may start
from verified changes integrated locally; a PR merge is not the default gate.
Actual deployment or external verification prerequisites still apply. Preserve
an already agreed PR-per-stage or merge gate when one exists.

## Receive, review, and integrate

1. Reconcile the worker result with its actual diff and workspace. Record the
   exact base and resulting revision, criteria evidence, limitations, and open
   issues. A completion message alone does not complete a stage.
2. Dispatch `feature-review` in a separate agent with the stage, relevant shared
   contracts, exact change range, code access, and evidence. Review both required
   behavior and code quality. Do not bias the reviewer with a preferred verdict.
   If independent review is unavailable, leave that gate pending; continue other
   independent work where useful.
3. Route confirmed findings using the categories above. Send scoped fixes back
   to the original worker when its context is still useful. Recheck the changed
   behavior and reassess affected review conclusions. Allow two repair rounds
   per unresolved issue by default; after that, record a blocker and the attempted
   approaches. Resume only when new evidence or direction changes the approach.
   A fresh worker alone does not reset the repair count.
4. Integrate reviewed changes one at a time in the integration workspace. Check
   the current base and resolve conflicts within the contract; send substantive
   integration edits through review again. Run the affected integration and
   regression checks against the combined code. Worker tests do not prove the
   combined result works. The coordinator controls integration and shared records.
5. Mark a stage done only when its required evidence, review, and integration
   are complete for the recorded code. Persist the checkpoint, then dispatch
   newly unblocked work from that integration state without waiting for unrelated
   workers to finish. Never start a dependent stage on a worker's unintegrated result.

During execution, if a worker needs to expand its write scope or use a conflicting
resource, stop that part of its work and reconcile allocations first. Worktree
isolation does not make conflicting contracts independent.

## Continue or finish

Keep the coordinator's context focused on intent, decisions, assignments, evidence
pointers, and the next action. Workers keep implementation logs in their context;
persist only the result needed for review and recovery. Report concise progress
at stage transitions and material discoveries. Do useful coordination while
workers run; use the host's completion/wait tools instead of busy polling.

On resume, reconcile the checkpoint with live agents, branches, commits, diffs,
and evidence before scheduling. Recover partial work in its existing workspace;
do not dispatch a duplicate worker because a completion message is missing.
Stale status requires investigation, not automatic success or a destructive reset.

A blocked stage leaves dependent stages waiting. Continue ready independent work.
When none can proceed, preserve partial changes and report the precise missing
decision, evidence, or environment and the next recovery action. Do not mark the
feature complete while any required gate remains pending. Respect user budgets
and host limits; save progress before stopping when possible.

After all stages are integrated, review the feature as a whole and demonstrate
the original success criteria across its real integration boundaries. Use an
independent reviewer when available. Add an in-scope repair stage if this exposes
a gap. Finish with the delivered behavior, verification and limitations, links to
the change, and any remaining user assessment or authorized publication step.
