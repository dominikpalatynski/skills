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

A typical workflow is **shape → plan → step → review**, repeating implementation
and review for subsequent stages. Each skill can also be used independently.

Feature Plan includes a [stage template](feature-plan/assets/stage.md).

## Repository structure

Each skill lives in its own directory with a `SKILL.md` file and any supporting
assets or metadata. Keep the directory intact when copying a skill manually so
supporting files and relative links remain available.
