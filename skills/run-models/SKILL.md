---
name: run-models
description: Run Replicate models via predictions and webhooks
---

## Docs

- Reference docs: https://replicate.com/docs/llms.txt
- HTTP API schema: https://api.replicate.com/openapi.json
- Set an `Accept: text/markdown` header when requesting docs pages to get a Markdown response.

## Workflow

- Create a prediction with POST /v1/predictions.
- Poll for completion, use a webhook, or set `Prefer: wait` for fast models.
- Add a webhook URL at creation time when you want async delivery.
- Read model schemas to validate inputs before sending requests.
- Return output when the prediction status is "succeeded".

## Guidelines

- Use HTTPS URLs for file inputs; avoid base64 when possible.
- POST /v1/predictions supports both official and community models.
- Run predictions concurrently rather than serially.
- Webhooks are a good way to receive and store outputs.
- Output file URLs expire after 1 hour; back them up if needed.
