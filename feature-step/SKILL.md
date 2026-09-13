---
name: feature-step
description: Implement or resume one feature stage from a short specification, description, or existing PR. Deliver an observable result, tests, and a demonstration ready for user review. Use for staged delivery; does not automatically execute the entire parent specification.
---

# Feature Step

One invocation implements one stage by default. The user retains control over
direction and outcome while the agent works independently within the agreed scope.
Earlier decisions, authorization, and an explicit request for broader work take
precedence over this skill's default boundaries.

Use the repository's tools and commands. OM, OpenSpec, and their state files
are not dependencies of this workflow. Run such a pipeline only when requested
by the user, including when an older specification shows examples of invoking it.

## Start or resume

1. Read the stage, relevant parts of the parent contract, local instructions,
   and current code. The stage document defines scope; a reference to the whole
   feature does not expand it. For a small change, scope and criteria in the
   conversation are sufficient without a new document.
2. Check dependencies and the environment required for the demonstration. If only
   a large specification is supplied, select the first ready, unfinished stage
   from its map and state the selection. Ask only when scope cannot be determined
   from context. Fill in missing details before coding, within the requested scope.
3. Inspect the existing branch, worktree, diff, and PR for this stage. Resume the
   same work; an old summary or checked box in a specification is not proof of
   completion. Preserve other people's work and unrelated changes.
4. For a new stage, prefer a short-lived branch from the current base branch and
   an isolated worktree when needed. Determine the base from the repository;
   assume neither `main` nor a particular pipeline configuration. By default,
   one stage has one PR, and the next dependent stage starts after its predecessor merges.

Start by stating the current goal, finish line, and first action. Keep one stage
active. Reconstruct progress from code, git, the stage document, and the existing
PR; do not add mandatory execution plans or separate files for resuming work.

## Implement

Implement the scope together with meaningful failure handling. Make routine
technical decisions and fixes independently. Return to the user when new evidence
requires a material change to product behavior, a shared contract, or scope.
Prepare a concrete recommendation; continue independent work already agreed upon.

If the stage proves too large, propose the smallest useful split and explain
what has already been done. Do not silently expand the assignment or declare
the whole stage complete after implementing only part of it. Keep new ideas
briefly in "Later" in the existing document or conversation. Update affected
decisions and future stages when evidence warrants it, without rewriting the whole plan.

## Verify

- Run checks appropriate to the change and required by the repository. Add
  behavior tests where needed; do not write tests that mirror the implementation
  merely to increase the number of checks.
- Demonstrate the primary success and a meaningful failure, and check affected
  existing behavior. Use a working view for UI; show appropriate requests,
  results, or observations for APIs, CLIs, and infrastructure.
- Map evidence to acceptance criteria. Give the command or action, result,
  environment, and limitations. Distinguish code checks, deployment, and live
  behavior; a test double or infrastructure plan does not prove an external service works.
- If the environment is unavailable, complete available checks and identify
  unverified criteria. Do not mark the goal as achieved; code may be ready for
  review while the demonstration remains pending.

Prepare the change and evidence for a separate AI review, such as `$feature-review`.
If that review was requested and an independent reviewer is available, provide
scope, contract, and diff. Label your own checks as your own; do not present them
as an independent review. Fix confirmed issues within the stage's scope and
recheck affected behavior. Explicitly leave independent review pending if it
has not been performed.

## Handoff

Record results, the demonstration, and outstanding items in the existing PR or
conversation summary. Create or update a PR when publication was requested or
is part of the agreed workflow. This skill does not itself authorize additional
external actions. Provide short instructions on what the user should run or
inspect and what result to expect. Explain material deviations from the plan.

Finish with **Done**, **Verified**, **For your review**, and **Next step**,
using the user's language. Link to the change and give one concrete action
that makes it easy to resume. The default finish line is a verified change
ready for user review; merging and starting another stage require a separate
request unless they have already been requested.
