---
name: find-models
description: Find Replicate models and curated collections
---

## Docs

- Reference docs: https://replicate.com/docs/llms.txt
- HTTP API schema: https://api.replicate.com/openapi.json
- Set an `Accept: text/markdown` header when requesting docs pages to get a Markdown response.

## Workflow

- Use search and collections endpoints from the API schema.
- Prefer curated collections for vetted models.
- Use the "official" collection when you need stable interfaces.
- Check model metadata for inputs, outputs, and pricing.

## Guidelines

- Avoid listing all models via API; use targeted queries.
- Collections are curated by Replicate staff.
- Official models are maintained by Replicate and are always running.
- Official models have stable interfaces and predictable output pricing.
- Community models can have cold-start time.
- Always-on deployments of community models pay for uptime.
