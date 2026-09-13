# P01 — Name the observable outcome

Parent specification: link to the shared contract, if one exists.
Dependencies: required stages and demonstration prerequisites.
Readiness: ready to implement, or the specific missing decision / dependency.

## Goal

One sentence describing what can be run or checked after this stage.

## Scope and boundaries

- Behavior and contracts implemented in this stage.
- Owner of the change and relevant integration points.
- What remains outside the stage; links to shared rules instead of copies.
- Deliberate simplifications and their practical cost, where relevant; what
  concrete need would justify revisiting them.

## Implementation steps

A few concrete steps needed to reach the goal, including failure handling.

## Criteria and evidence

| Criterion | How to verify | Expected result |
| --- | --- | --- |
| Primary success | Concrete action or test | Observable outcome |
| Meaningful failure | Trigger a failure at the operation boundary | Rejection / recovery without violating the contract |
| Affected existing behavior | Relevant regression check | Preserved contract |

Provide the appropriate repository commands and required environment. Briefly
explain what the user should do or inspect to assess the result. During
implementation, a separate AI review compares requirements, the diff, and
evidence; do not fill in its result in advance.

## Integration and finish line

Describe the safe state after merging and any conditions for enabling the
feature that apply to this stage. Distinguish code, deployment, and verification
in the target environment. State when implementation of the stage is complete
and what remains for the user to assess. Execution results and outstanding
items belong in the PR or conversation summary.
