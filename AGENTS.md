# Replicate Skills: Agent Notes

## Purpose

This repo publishes Agent Skills documents for Replicate.

Keep it short and focused: human- and agent-readable guides for finding, comparing, running, building, and deploying models.

## Files that matter

- `skills/find-models/SKILL.md` covers discovery workflows.
- `skills/compare-models/SKILL.md` covers model evaluation.
- `skills/run-models/SKILL.md` covers prediction workflows.
- `skills/build-models/SKILL.md` covers Cog builds.
- `skills/deploy-models/SKILL.md` covers deployments and scaling.
- `.mcp.json` points to the remote MCP server.
- `.claude-plugin/` contains marketplace metadata for Claude Code.

## Editing guidelines

- Keep `SKILL.md` concise and practical. Prefer bullet lists over long prose.
- Treat `https://api.replicate.com/openapi.json` as the source of truth.
- Keep mentions of deprecated or unofficial endpoints out of the skill.
- Do not add language-specific client guidance unless explicitly requested.

## Linting

Lint before committing changes:

```
script/lint
```
