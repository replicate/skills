---
name: deploy-models
description: Push models with Cog and configure Replicate deployments
---

## Docs

- Cog docs: https://cog.run/llms.txt
- Replicate docs: https://replicate.com/docs/llms.txt
- HTTP API schema: https://api.replicate.com/openapi.json
- Set an `Accept: text/markdown` header when requesting docs pages to get a Markdown response.

## Workflow

- Use Cog to build and push a model image.
- Configure deployments in Replicate for hardware and scaling behavior.
- Use the API schema as the source of truth for deployment fields.
- Align deployment settings with expected throughput and cost.

## Guidelines

- Review models with GitHub repos in their metadata for deployment examples.
- Keep deployment settings aligned with model performance and cost targets.
- Prefer official models for stable deployment behavior.
- Use deployments when you need consistent uptime and predictable latency.
