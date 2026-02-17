---
name: build-models
description: Build Replicate models using Cog
---

## Docs

- Cog docs: https://cog.run/llms.txt
- Replicate docs: https://replicate.com/docs/llms.txt
- HTTP API schema: https://api.replicate.com/openapi.json
- Set an `Accept: text/markdown` header when requesting docs pages to get a Markdown response.

## Workflow

- Define your model in `cog.yaml` using the Cog schema.
- Implement the Predictor interface in Python and wire inputs and outputs.
- Build and test the image locally with Cog before pushing.
- Use the Cog docs as the source of truth for `cog.yaml` and Predictor APIs.

## Guidelines

- Focus on the `cog.yaml` schema and the Predictor API in the Cog docs.
- Cog is open source at https://github.com/replicate/cog if you need internals.
- Review Replicate models that link GitHub repos to learn existing Cog patterns.
- Use model repos as references for inputs, outputs, and packaging decisions.
- Keep `cog.yaml` minimal and explicit about build and runtime dependencies.
