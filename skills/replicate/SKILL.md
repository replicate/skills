---
name: replicate
description: >
  Run AI models on Replicate. Use when building apps that generate images, video, speech,
  music, or text, or when the user asks about Replicate models, predictions, or deployments.
  Covers model search, schema inspection, running predictions, collections, deployments,
  and multi-model pipelines.
---

# Replicate

Replicate lets you run AI models with a cloud API. Thousands of models for image generation, video, speech, music, text, and more.

## Docs

- Reference: <https://replicate.com/docs/llms.txt>
- OpenAPI schema: <https://api.replicate.com/openapi.json>
- MCP server: <https://mcp.replicate.com>
- Per-model docs: `https://replicate.com/{owner}/{model}/llms.txt`
- Set `Accept: text/markdown` when requesting docs pages for Markdown responses.

## Key concepts

- **Models** are identified as `owner/name` (e.g. `black-forest-labs/flux-2-klein-9b`).
- **Official models** are always warm, have stable APIs, and predictable pricing. Use `owner/name`.
- **Community models** require a version: `owner/name:version_id`. They cold-boot and can be slow.
- **Predictions** are individual model runs: `starting` → `processing` → `succeeded`/`failed`/`canceled`.
- **Deployments** are always-on instances of community models you manage.
- **Collections** are curated groups of models (e.g. `text-to-image`, `official`).

## Search for models

Use the search API to find models by task. It returns models, collections, and docs.

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  "https://api.replicate.com/v1/search?query=image+generation" | jq '[.models[:3][] | {name: .model.name, owner: .model.owner}]'
```

```python
import replicate

page = replicate.models.search("image generation")
for model in page.results[:3]:
    print(f"{model.owner}/{model.name}: {model.description}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const page = await replicate.models.search("image generation");
for (const model of page.results.slice(0, 3)) {
  console.log(`${model.owner}/${model.name}: ${model.description}`);
}
```

For deeper guidance on picking the right model, see [MODEL_SEARCH.md](references/MODEL_SEARCH.md).

## Get a model's schema

Always fetch a model's schema before running it. Schemas change.

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models/black-forest-labs/flux-2-klein-9b \
  | jq '.latest_version.openapi_schema.components.schemas.Input.properties | keys'
```

```python
import replicate

model = replicate.models.get("black-forest-labs", "flux-schnell")
schema = model.latest_version.openapi_schema["components"]["schemas"]["Input"]["properties"]
for name, prop in schema.items():
    print(f"  {name}: {prop.get('type', '?')} — {prop.get('description', '')}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const model = await replicate.models.get("black-forest-labs", "flux-schnell");
const schema =
  model.latest_version.openapi_schema.components.schemas.Input.properties;
for (const [name, prop] of Object.entries(schema)) {
  console.log(`  ${name}: ${prop.type || "?"} — ${prop.description || ""}`);
}
```

## Run a prediction

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait=60" \
  -d '{"version": "black-forest-labs/flux-2-klein-9b", "input": {"prompt": "a cat wearing a top hat", "num_outputs": 1}}' \
  https://api.replicate.com/v1/predictions | jq '{id, status, output}'
```

```python
import replicate

output = replicate.run(
    "black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a cat wearing a top hat", "num_outputs": 1},
)
for item in output:
    print(item.url)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const output = await replicate.run("black-forest-labs/flux-2-klein-9b", {
  input: { prompt: "a cat wearing a top hat", num_outputs: 1 },
});
console.log(output);
```

For polling, webhooks, streaming, file I/O, and concurrency patterns, see [PREDICTIONS.md](references/PREDICTIONS.md).

## Key rules

- **Always fetch the schema first.** Even popular models change their interfaces.
- **Validate inputs against schema constraints** — check `minimum`, `maximum`, `enum` values.
- **Don't set optional inputs without reason.** Let the model's defaults work.
- **Prefer official models.** They're warm, stable, and predictably priced.
- **Use HTTPS URLs for file inputs.** Base64 works but is slower.
- **Run predictions concurrently.** Don't wait for one to finish before starting the next.
- **Output file URLs expire in 1 hour.** Back them up to R2/S3 if you need to keep them.

## Browse collections

Collections are curated model groups maintained by Replicate. The `official` collection has always-warm models.

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/collections/official | jq '{name, slug, description}'
```

```python
import replicate

collection = replicate.collections.get("official")
print(f"{collection.name}: {collection.description}")
for model in collection.models[:3]:
    print(f"  {model.owner}/{model.name}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const collection = await replicate.collections.get("official");
console.log(`${collection.name}: ${collection.description}`);
for (const model of collection.models.slice(0, 3)) {
  console.log(`  ${model.owner}/${model.name}`);
}
```

For the full collection list and API details, see [COLLECTIONS.md](references/COLLECTIONS.md).

## Multi-model workflows

Complex tasks often chain multiple models. Use parallel predictions for speed. See [WORKFLOWS.md](references/WORKFLOWS.md) for pipeline patterns including video generation, image editing, and audio translation.

## References

| Reference | Content |
|-----------|---------|
| [HTTP_API.md](references/HTTP_API.md) | Full HTTP API reference — endpoints, auth, pagination, errors |
| [MODEL_SEARCH.md](references/MODEL_SEARCH.md) | Finding models, reading schemas, picking the right model |
| [COLLECTIONS.md](references/COLLECTIONS.md) | Browsing curated model collections, full collection list |
| [PREDICTIONS.md](references/PREDICTIONS.md) | Running models — official vs community, polling, webhooks, files, concurrency |
| [DEPLOYMENTS.md](references/DEPLOYMENTS.md) | Custom always-on deployments for community models |
| [WORKFLOWS.md](references/WORKFLOWS.md) | Multi-model pipeline patterns — video, image editing, audio, chaining |
| [CLOUDFLARE_WORKERS.md](references/CLOUDFLARE_WORKERS.md) | Using Replicate from Cloudflare Workers |
| [CLOUDFLARE_WORKFLOWS.md](references/CLOUDFLARE_WORKFLOWS.md) | Multi-step Replicate pipelines with Cloudflare Workflows |
