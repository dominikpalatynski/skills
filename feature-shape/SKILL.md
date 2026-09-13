---
name: feature-shape
description: Explore a feature idea through conversation, repository analysis, and comparison of approaches; prepare a concise brief. Use before specification or to examine a product or architecture decision in depth. Use feature-plan for an existing brief and delivery planning.
---

# Feature Shape

Help the user understand the problem and choose a direction. Leave room for
open conversation and deeper examination of a decision before planning delivery.
The user's instructions, earlier decisions, and requested scope take precedence
over this skill's default workflow.

## Explore

1. Establish what should change for the user and how they will recognize success.
   Reuse the conversation, existing brief, and code; do not repeat answered questions.
2. Check ownership, local instructions, and the main integration points.
   Distinguish facts confirmed in the repository from assumptions and recommendations.
3. Compare viable approaches, including a simpler solution or keeping the current
   behavior when that meets the need. Explain meaningful costs and consequences;
   recommend an approach.
4. When asked "how exactly?", trace a concrete path: data, owners, calls,
   persisted state, and failure behavior. Use an example or small diagram when
   it helps the user assess the approach. Check current external documentation
   when a decision depends on a mechanism's actual guarantees.
5. Establish the smallest useful scope and what belongs later. Turn an unknown
   that could change the architecture into a specific question to investigate,
   and identify the evidence needed to resolve it.

Ask about one meaningful decision at a time, preferably with a recommendation.
Continue analysis that does not depend on the answer. Resolve routine technical
details independently. Do not treat silence as acceptance. Keep side ideas in
a short "Later" section without expanding the current work.

## Brief

When the direction is clear enough, assemble concise input for planning:

- the goal and an example of the expected behavior;
- initial scope and exclusions;
- the recommended approach, a relevant alternative, and the reason for the choice;
- confirmed integration points;
- accepted decisions, proposals, and open questions;
- success criteria and the most important things to verify.

The brief may remain in the conversation. Save it when the user requests a
document or durable input for another session; follow the repository's existing
brief location and conventions. Update an existing brief instead of creating
additional versions alongside it. Do not add a process log or execution plan.

## Finish

Present the recommendation and decisions that need the user's input. A brief
does not itself start implementation. When moving to a specification,
`$feature-plan` can use the conversation or brief path; it is not a required
dependency. Preserve any existing authorization for subsequent steps.

Finish briefly, in the user's language, using these fields: **Done**,
**Verified**, **For your review**, **Next step**. Name one action in the last field.
