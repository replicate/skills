# Replicate Skills: Agent Notes

## Purpose

This repo publishes Agent Skills for Replicate: a main skill document plus focused reference docs covering predictions, model search, collections, workflows, deployments, Cloudflare integration, and the HTTP API.

## Files that matter

- `skills/replicate/SKILL.md` — the main skill (overview, common patterns, reference table).
- `skills/replicate/references/*.md` — detailed reference docs linked from SKILL.md.
- `script/lint` — validates the skill and lints Python with ruff.
- `script/test_snippets.py` — extracts and runs every code snippet from the markdown files.
- `test/fixtures/` — test assets (e.g. images for workers that accept file uploads).
- `.mcp.json` — points to the remote MCP server.
- `.claude-plugin/` — marketplace metadata for Claude Code.

## Editing guidelines

- Keep `SKILL.md` concise. Detailed examples go in `references/`.
- Every code snippet must be runnable. The test runner executes them all.
- Snippets starting with `// worker.js` or `// workflow.js` are tested via `wrangler dev`.
- Snippets whose worker reads `request.blob()` or `request.arrayBuffer()` get a test image POSTed automatically.
- Treat `https://api.replicate.com/openapi.json` as the source of truth.
- Do not add language-specific client guidance unless explicitly requested.

## Linting

```
script/lint
```

## Testing

Runs all code snippets (bash, python, javascript) from every markdown file:

```
REPLICATE_API_TOKEN=... python script/test_snippets.py
```

Syntax check only (no API calls):

```
REPLICATE_API_TOKEN=... python script/test_snippets.py --syntax-only
```

Test a single reference file:

```
REPLICATE_API_TOKEN=... python script/test_snippets.py --include references/CLOUDFLARE_WORKERS.md
```
