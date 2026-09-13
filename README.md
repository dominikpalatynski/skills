# Skills

A collection of reusable skills for AI coding agents, organized by workflow.

## Installation

Install all skills with the [Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add dominikpalatynski/skills --skill '*'
```

Follow the prompts to choose your agent and installation scope.

To install a specific skill, use its name:

```bash
npx skills add dominikpalatynski/skills --skill feature-plan
```

## Skills

### Feature development

Skills for exploring ideas and delivering features in small, verifiable stages.

| Skill | Purpose |
| --- | --- |
| [Feature Shape](feature-shape/SKILL.md) | Explore an idea, compare approaches, and prepare a concise brief. |
| [Feature Plan](feature-plan/SKILL.md) | Turn a brief or specification into small stages with observable goals and verification. |
| [Feature Step](feature-step/SKILL.md) | Implement or resume one stage and demonstrate the result. |
| [Feature Review](feature-review/SKILL.md) | Review a design, stage breakdown, or implementation and identify concrete gaps. |
| [Feature Loop](feature-loop/SKILL.md) | Coordinate all remaining stages, delegate independent work, and verify the integrated feature against its intent. |

A typical workflow is **shape → plan → step → review**, repeating implementation
and review for subsequent stages. Each skill can also be used independently.

When the request includes both design and delivery planning, Feature Shape
continues into Feature Plan without requiring separate skill invocations.
The agent develops the proposal and technical details, asking for decisions
that materially change the product, scope, or accepted trade-offs. Requests
limited to discussion, review, or one implementation stage retain those boundaries.

Feature Plan includes a [stage template](feature-plan/assets/stage.md).

For autonomous delivery across stages, use Feature Loop with a feature brief or
specification, for example:

```text
Use $feature-loop to finish docs/features/export/spec.md. Fill missing stage
details and delegate independent stages to subagents. Integrate and verify the
whole feature, keeping at most two stages active.
```

Feature Loop maintains the plan, assigns isolated workspaces, coordinates review
and fixes, and continues when dependencies become ready. Its small read-only
Python 3.9+ helper checks the execution checkpoint and suggests compatible work;
the agent checks actual behavior and evidence. Existing authorization governs
publication and deployment. A blocked stage does not stop independent work, and
the checkpoint supports resuming a later invocation; the skill itself does not
restart terminated sessions.

## Repository structure

Each skill lives in its own directory with a `SKILL.md` file and any supporting
assets or metadata. Keep the directory intact when copying a skill manually so
supporting files and relative links remain available.
