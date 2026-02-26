# Finding and Choosing Models

## Search API

The search endpoint finds models, collections, and docs by text query:

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  "https://api.replicate.com/v1/search?query=text+to+speech" | jq '[.models[:3][] | {name: .model.name, owner: .model.owner, runs: .model.run_count}]'
```

```python
import replicate

page = replicate.models.search("text to speech")
for model in page.results[:3]:
    print(f"{model.owner}/{model.name} — {model.run_count} runs")
    print(f"  {model.description}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const page = await replicate.models.search("text to speech");
for (const model of page.results.slice(0, 3)) {
  console.log(`${model.owner}/${model.name} — ${model.run_count} runs`);
  console.log(`  ${model.description}`);
}
```

Search returns metadata for each model result including `tags`, `generated_description`, and `run_count`.

The search also returns matching collections. Use the [collections API](COLLECTIONS.md) to browse curated model groups.

## Per-model docs

Every model has an LLM-readable docs page:

```
https://replicate.com/{owner}/{model}/llms.txt
```

For example: <https://replicate.com/black-forest-labs/flux-2-klein-9b/llms.txt>

## Reading model schemas

Every model exposes its input/output schema via the models API:

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models/black-forest-labs/flux-2-klein-9b \
  | jq '.latest_version.openapi_schema.components.schemas.Input.properties | to_entries[] | {name: .key, type: .value.type, description: .value.description}'
```

```python
import replicate

model = replicate.models.get("black-forest-labs", "flux-schnell")
input_schema = model.latest_version.openapi_schema["components"]["schemas"]["Input"]
for name, prop in input_schema["properties"].items():
    required = name in input_schema.get("required", [])
    print(f"{'*' if required else ' '} {name}: {prop.get('type', '?')} — {prop.get('description', '')}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const model = await replicate.models.get("black-forest-labs", "flux-schnell");
const inputSchema =
  model.latest_version.openapi_schema.components.schemas.Input;
const required = inputSchema.required || [];
for (const [name, prop] of Object.entries(inputSchema.properties)) {
  console.log(
    `${required.includes(name) ? "*" : " "} ${name}: ${prop.type || "?"} — ${prop.description || ""}`,
  );
}
```

The schema path is: `model.latest_version.openapi_schema.components.schemas.Input.properties`

Each property may include:
- `type` — data type (`string`, `integer`, `number`, `boolean`)
- `description` — what the input does
- `default` — default value
- `minimum` / `maximum` — numeric bounds
- `enum` — allowed values
- `format` — e.g. `uri` for file inputs
- `x-order` — display order on the model page

## Validating inputs

After fetching a schema, validate your inputs:

- Check `required` fields are present
- Check numeric values are within `minimum`/`maximum` bounds
- Check string values are in `enum` if specified
- Don't set optional inputs unless you have a reason — let defaults work

If unsure about a parameter value, check the model's `default_example` (returned by the models.get endpoint) to see what inputs were used in a working prediction.

## Picking the right model

- **Prefer official models.** They're always warm (no cold boot), have stable APIs, and predictable pricing. They're in the `official` collection.
- **Prefer the latest version.** If search returns Kling 2.5 and Kling 3.0, use Kling 3. Use Nano Banana Pro instead of Nano Banana. Use FLUX.1 Pro over FLUX.1 Schnell for quality.
- **Run count can be misleading.** Old models accumulate runs over time but may be outdated. A model with 10M runs from 2023 is likely worse than a model with 100K runs from 2025.
- **Prefer recently released models.** The AI space moves fast. Most of the thousands of models on Replicate are from the past five years; many are outdated.
- **Check model tags.** Search results include tags like `image-generation`, `video`, `audio` to help filter.

## Listing model versions

Each model can have multiple versions. Official models route to the latest automatically, but community models require a specific version ID. Only community models expose a version list.

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/models/stability-ai/sdxl/versions | jq '[.results[:3][] | {id: .id, created_at: .created_at}]'
```

```python
import replicate

model = replicate.models.get("stability-ai", "sdxl")
versions = model.versions.list()
for v in versions.results[:3]:
    print(f"{v.id} — created {v.created_at}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const versions = await replicate.models.versions.list("stability-ai", "sdxl");
for (const v of versions.results.slice(0, 3)) {
  console.log(`${v.id} — created ${v.created_at}`);
}
```
