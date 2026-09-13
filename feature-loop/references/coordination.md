# Coordination contract

## Shared records

The brief preserves accepted intent; the specification owns the current contract
and stage map. The coordinator is the sole writer of shared planning and run
records. Workers propose changes to them in their results.

For a loop, keep a compact execution checkpoint in the existing specification
and a short evidence/result section in each implemented stage document (or a link
to the existing PR evidence). This is the loop-specific extension to the default
`feature-plan` and `feature-step` reporting convention. Do not create a second
specification, parallel backlog, or empty documents for future stages.

If the repository already has machine-readable tracking, use it as the execution
checkpoint and check the same invariants there; do not maintain a duplicate just
to use the helper. Otherwise add one fenced `feature-loop` JSON block to the
current specification. This block is the execution view of the delivery map;
update both together when dependencies or scope change. Keep behavior, contracts,
and criteria in their existing prose, referenced by `stage`.

Example (adapt IDs, paths, scopes, and evidence to the project):

```feature-loop
{
  "version": 1,
  "max_active_stages": 2,
  "stages": [
    {
      "id": "P01",
      "stage": "01-export-contract.md",
      "depends_on": [],
      "status": "pending",
      "ready": true,
      "writes": ["src/export/types.ts"],
      "resources": []
    },
    {
      "id": "P02",
      "stage": "spec.md#p02",
      "depends_on": ["P01"],
      "status": "pending",
      "ready": false,
      "writes": ["src/export/csv/", "tests/export/csv/"],
      "resources": []
    },
    {
      "id": "P03",
      "stage": "spec.md#p03",
      "depends_on": ["P01"],
      "status": "pending",
      "ready": false,
      "writes": ["src/export/json/", "tests/export/json/"],
      "resources": []
    }
  ]
}
```

Resolve `stage` relative to the specification. An outline may point to an existing
spec section (for example `spec.md#p03`) until a detailed stage is needed.

Run, using the installed skill's absolute path:

```sh
python3 /path/to/feature-loop/scripts/loop_state.py /path/to/spec.md
```

The helper reads exactly one `feature-loop` fence, validates it, and prints JSON:
`active`, `eligible`, `selected`, `waiting`, and `all_done`. It supports a plain
JSON checkpoint too, if that is the repository's existing format. It never edits
files, starts agents, reserves work, changes Git, or verifies implementation.
Exit 0 means structurally valid; exit 2 reports invalid input. `all_done` only
describes records; the coordinator still performs final feature verification.

## Checkpoint fields and transitions

- `version`: `1`. `max_active_stages`: positive integer, normally `2`.
- `stages`: nonempty list in preferred scheduling order. `id` is unique and
  stable; `depends_on` lists existing IDs and must form an acyclic graph.
- `ready`: true only after the stage's decisions, detail, scope, and feasible
  verification have been checked. Dependencies are checked separately. Leave
  outlines false. Reassess readiness when contracts or prerequisites change.
- `writes`: repository-relative files or directories, with `/` suffix for a
  directory. Use `.` to reserve the whole repository when scope is uncertain;
  use `[]` only for work that does not write repository files. No globs.
- `resources`: exclusive mutable resource names, such as `test-db:exports` or
  `port:4100`. Shared contracts also need coordination even with disjoint files.
- `status`: `pending`, `running`, `review`, `integrating`, `done`, or `blocked`.
  `running`, `review`, and `integrating` reserve an active-stage slot and scopes.
- For an active stage, `assignment` records `owner`, absolute `workspace`, and
  `base_ref`. Also record `branch` when using Git. Reserve the assignment before
  spawning with an owner such as `dispatching:P02`, then replace it with the live
  agent ID. On interruption, reconcile this reservation before redispatching.
- For `done`, `result` must contain `change_ref`, a nonempty `evidence` list,
  `review_ref`, and `integration_ref`. These point to actual code and recorded
  checks, review, and combined-code verification; they are not attestations
  manufactured to satisfy validation. Use immutable Git revisions where available.
- For `blocked`, record a nonempty `blocker` with the unresolved condition. Stop
  its worker and release resources before changing to this state. Preserve its
  assignment, partial changes, and repair count for recovery.

Normal transitions: pending → running → review → integrating → done. Fixes move
review back to running. Any unfinished stage can become blocked. After resolving
a blocker, resume the appropriate phase on the preserved work. Never skip review
or integration just because a worker exited successfully.

### Contract invalidation

When an accepted contract changes or evidence invalidates a prerequisite, first
identify the directly affected stages and all their transitive dependents.
Pause dispatch for that set and stop its live workers before releasing scopes.
Preserve commits, partial diffs, assignments, and prior evidence in their stage
records; label previous results with the contract/code revision they covered.

In one coordinator update, change every stage in that set, including previously
done stages, to `pending` with `ready: false`. Move any old checkpoint `result`
references into the stage's historical evidence section and remove `result`
from its current checkpoint entry. For a stage requiring a user decision or an
unavailable environment, use `blocked` with the reason instead. Changing only
`ready` on a done stage is invalid. Keep unaffected branches unchanged.

Update the affected stage contracts and recheck readiness. Reuse and reconcile
their preserved workspaces; do not rebuild completed code merely because its
evidence became stale. A previously integrated implementation that still meets
the revised contract can go through review and combined-code verification again
without a code change. Record fresh results before unlocking its dependents.

For a new regression under an unchanged contract, a repair stage can instead
depend on the already integrated stages and carry every affected acceptance
criterion. Earlier records describe their recorded revisions; the repair and
final feature checks must establish that the current combined code works.

The helper checks that active and done stages have done dependencies, that active
assignments and result references are present, and that active scopes do not
overlap. It greedily selects eligible pending stages in map order while respecting
capacity, active scopes, and earlier selections. `eligible` means ready with done
dependencies; `selected` also fits current allocations. Re-run after recording
each actual allocation; the helper itself provides no concurrent locking.

## Worker packet and result

Give the worker only:

- one stage's scope, finish line, exclusions, and relevant shared contracts;
- exact contract revision or snapshot, including any relevant uncommitted changes;
- absolute assigned worktree, branch/base revision, owned write paths, and test
  resources; require commands to run there and local instructions to be read;
- verification actions and expected results, including real vs simulated boundaries;
- instruction to use `feature-step`, remain within this stage, and send questions
  or scope changes to the coordinator; no further subagents, shared-document edits,
  publication, integration, or selection of subsequent stages;
- instruction to commit only its own changes when the run authorizes local
  commits, otherwise return the exact diff; no broad staging or resetting other work.

Record results in the existing stage evidence section through the coordinator:
status (`ready_for_review`, `needs_context`, or `blocked`), base and change
revisions, changed paths, criterion → action → result → environment, limitations,
findings affecting intent/plan, and the next action. The coordinator also records
the reviewer, reviewed revision, remaining findings, repair attempts, integration
revision, and combined-code checks. Store long logs only when needed as evidence.

If the worker's requested write scope expands, reconcile it with other active
assignments before allowing those edits. A free worker slot never overrides an
unsatisfied dependency, missing decision, stale contract, or unavailable resource.

## Reviewer packet

Use a separate agent with `feature-review`. Supply the stage, binding contracts,
the exact base-to-result change range (including every commit and relevant
uncommitted change), a stable workspace containing that code, and evidence paths.
The implementer must not modify the reviewed snapshot during review. Ask for
specification compliance, concrete defects, missing evidence, and implications
for the remaining plan. The reviewer reports findings without editing shared
state or starting agents. Fixes invalidate affected conclusions and evidence.

Keep code-level stage review and the final cross-stage review distinct. The
latter checks the original goal, omissions across stage boundaries, and the
integrated behavior. Missing live evidence remains pending even when local tests
and isolated stage reviews pass.
