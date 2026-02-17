---
name: compare-models
description: Compare Replicate models for fit, cost, and reliability
---

## Docs

- Reference docs: https://replicate.com/docs/llms.txt
- HTTP API schema: https://api.replicate.com/openapi.json
- Set an `Accept: text/markdown` header when requesting docs pages to get a Markdown response.

## Workflow

- Fetch model schemas and compare required inputs and outputs.
- Compare pricing, speed, and reliability from model metadata.
- Prefer official models when you need stable interfaces.
- Use collections to narrow the shortlist before deep comparison.
- Run a small set of predictions to compare output quality.

## Guidelines

- Verify output types match downstream requirements.
- Official models have predictable output pricing and stable APIs.
- Consider cold-start behavior for community models.
