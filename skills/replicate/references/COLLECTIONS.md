# Collections

Collections are curated groups of models maintained by Replicate staff. They're a good way to discover vetted models for specific tasks.

## List all collections

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/collections | jq '[.results[] | {slug, name}]'
```

```python
import replicate

page = replicate.collections.list()
for collection in page.results:
    print(f"{collection.slug}: {collection.name} — {collection.description}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const page = await replicate.collections.list();
for (const collection of page.results) {
  console.log(
    `${collection.slug}: ${collection.name} — ${collection.description}`,
  );
}
```

## Get a collection

Returns the collection metadata and a list of its models:

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/collections/text-to-image | jq '{name, slug, description, model_count: (.models | length)}'
```

```python
import replicate

collection = replicate.collections.get("text-to-image")
print(f"{collection.name}: {collection.description}")
for model in collection.models[:3]:
    print(f"  {model.owner}/{model.name}")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const collection = await replicate.collections.get("text-to-image");
console.log(`${collection.name}: ${collection.description}`);
for (const model of collection.models.slice(0, 3)) {
  console.log(`  ${model.owner}/${model.name}`);
}
```

The response includes `full_description` (Markdown) and a `models` array with full model objects.

## The `official` collection

The `official` collection contains models that are always warm, have stable APIs, and predictable per-run pricing. Always prefer official models when available.

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/collections/official | jq '{name, model_count: (.models | length)}'
```

## Available collections

To see the current list of collections, use the API to [list all collections](#list-all-collections).

The search API also returns matching collections alongside model results.
