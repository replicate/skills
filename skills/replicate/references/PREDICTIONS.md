# Running Predictions

## Official vs community models

**Official models** (`owner/name` format):
- Always warm — no cold-boot wait
- Stable API interfaces
- Predictable per-run pricing
- Maintained by Replicate staff

**Community models** (`owner/name:version_id` format):
- Can cold-boot (seconds to minutes for a new worker to start)
- You must pin a specific version ID
- Maintained by the model author — interfaces may change
- Can be made always-warm with a [deployment](DEPLOYMENTS.md)

The `POST /v1/predictions` endpoint handles both. Pass `version` as `owner/name` for official models or `owner/name:version_id` for community models.

## Create a prediction (async)

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version": "black-forest-labs/flux-2-klein-9b", "input": {"prompt": "a red panda in a bamboo forest", "num_outputs": 1}}' \
  https://api.replicate.com/v1/predictions | jq '{id, status}'
```

```python
import replicate

prediction = replicate.predictions.create(
    model="black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a red panda in a bamboo forest", "num_outputs": 1},
)
print(prediction.id, prediction.status)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const prediction = await replicate.predictions.create({
  model: "black-forest-labs/flux-2-klein-9b",
  input: { prompt: "a red panda in a bamboo forest", num_outputs: 1 },
});
console.log(prediction.id, prediction.status);
```

## Poll for results

```python
import replicate
import time

prediction = replicate.predictions.create(
    model="black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a red panda in a bamboo forest", "num_outputs": 1},
)
while prediction.status not in ("succeeded", "failed", "canceled"):
    time.sleep(1)
    prediction = replicate.predictions.get(prediction.id)

print(prediction.status)
if prediction.output:
    for url in prediction.output:
        print(url)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

let prediction = await replicate.predictions.create({
  model: "black-forest-labs/flux-2-klein-9b",
  input: { prompt: "a red panda in a bamboo forest", num_outputs: 1 },
});
while (!["succeeded", "failed", "canceled"].includes(prediction.status)) {
  await new Promise((r) => setTimeout(r, 1000));
  prediction = await replicate.predictions.get(prediction.id);
}
console.log(prediction.status);
if (prediction.output) {
  for (const url of prediction.output) {
    console.log(url);
  }
}
```

## Synchronous mode with `Prefer: wait`

Hold the connection open for up to 60 seconds. If the model finishes in time, the response includes the completed prediction with `output` populated.

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait=60" \
  -d '{"version": "black-forest-labs/flux-2-klein-9b", "input": {"prompt": "a red panda in a bamboo forest", "num_outputs": 1}}' \
  https://api.replicate.com/v1/predictions | jq '{id, status, output}'
```

The Python SDK's `replicate.run()` uses sync mode by default with a 60-second timeout.

If the model doesn't finish in time, the response returns the prediction in its current state. The `Location` response header and `urls.get` field both point to the polling URL.

## `replicate.run()` — convenience wrapper

`replicate.run()` creates a prediction, waits for it, and returns the output directly. It uses sync mode with a 60-second timeout.

```python
import replicate

output = replicate.run(
    "black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a red panda in a bamboo forest", "num_outputs": 1},
)
for item in output:
    print(item.url)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const output = await replicate.run("black-forest-labs/flux-2-klein-9b", {
  input: { prompt: "a red panda in a bamboo forest", num_outputs: 1 },
});
console.log(output);
```

## File inputs

Prefer HTTPS URLs for file inputs. Base64 is supported but slower and increases request size.

```python
import replicate

output = replicate.run(
    "black-forest-labs/flux-kontext-pro",
    input={
        "prompt": "make it look like a watercolor painting",
        "input_image": "https://picsum.photos/id/237/200/300.jpg",
    },
)
print(output.url)
```

Output file URLs expire after 1 hour. Download and store them immediately if you need to keep them.

## Concurrent predictions

Fire off multiple predictions in parallel. Don't wait for one to finish before starting the next.

```python
import replicate
import time

prompts = [
    "a red panda eating a bamboo sandwich",
    "a blue parrot riding a bicycle",
    "a green iguana playing chess",
]

predictions = [
    replicate.predictions.create(
        model="black-forest-labs/flux-2-klein-9b",
        input={"prompt": p, "num_outputs": 1},
    )
    for p in prompts
]

results = {}
while len(results) < len(predictions):
    time.sleep(1)
    for pred in predictions:
        if pred.id not in results:
            p = replicate.predictions.get(pred.id)
            if p.status in ("succeeded", "failed", "canceled"):
                results[pred.id] = p

for pred in results.values():
    print(pred.status, pred.output)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const prompts = [
  "a red panda eating a bamboo sandwich",
  "a blue parrot riding a bicycle",
  "a green iguana playing chess",
];

const predictions = await Promise.all(
  prompts.map((prompt) =>
    replicate.predictions.create({
      model: "black-forest-labs/flux-2-klein-9b",
      input: { prompt, num_outputs: 1 },
    }),
  ),
);

const poll = async (id) => {
  let pred = await replicate.predictions.get(id);
  while (!["succeeded", "failed", "canceled"].includes(pred.status)) {
    await new Promise((r) => setTimeout(r, 1000));
    pred = await replicate.predictions.get(id);
  }
  return pred;
};

const results = await Promise.all(predictions.map((p) => poll(p.id)));
for (const result of results) {
  console.log(result.status, result.output);
}
```

## Webhooks

Set `webhook` on the prediction to receive a POST when it completes. Use `webhook_events_filter` to receive only certain events.

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "black-forest-labs/flux-2-klein-9b",
    "input": {"prompt": "a red panda in a bamboo forest", "num_outputs": 1},
    "webhook": "https://example.com/webhook",
    "webhook_events_filter": ["completed"]
  }' \
  https://api.replicate.com/v1/predictions | jq '{id, status}'
```

Webhook events: `start`, `output`, `logs`, `completed`.

Replicate signs webhook requests. Validate using the `Webhook-ID`, `Webhook-Timestamp`, and `Webhook-Signature` headers. Get the signing secret from `GET /v1/webhooks/default/secret`.

## Cancel a prediction

```python
import replicate

prediction = replicate.predictions.create(
    model="black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a red panda in a bamboo forest", "num_outputs": 1},
)
cancelled = replicate.predictions.cancel(prediction.id)
print(cancelled.status)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const prediction = await replicate.predictions.create({
  model: "black-forest-labs/flux-2-klein-9b",
  input: { prompt: "a red panda in a bamboo forest", num_outputs: 1 },
});
const cancelled = await replicate.predictions.cancel(prediction.id);
console.log(cancelled.status);
```

## Prediction lifetime (auto-cancel)

Set `lifetime` to cancel predictions that run too long:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "version": "black-forest-labs/flux-2-klein-9b",
    "input": {"prompt": "a red panda in a bamboo forest", "num_outputs": 1},
    "lifetime": "5m"
  }' \
  https://api.replicate.com/v1/predictions | jq '{id, status}'
```

Accepts `30s`, `5m`, `1h`, `1h30m45s`. Measured from the creation time.

## Streaming (SSE)

Models that support streaming (typically language models) include a `stream` URL in the response. Use SSE to receive incremental output.

```python
import replicate

prediction = replicate.predictions.create(
    model="meta/meta-llama-3-8b-instruct",
    input={"prompt": "write a haiku about mountains"},
    stream=True,
)
for event in prediction.stream():
    print(str(event), end="", flush=True)
print()
```

## Async Python

```python
import asyncio
import replicate

async def main():
    output = await replicate.async_run(
        "black-forest-labs/flux-2-klein-9b",
        input={"prompt": "a red panda in a bamboo forest", "num_outputs": 1},
    )
    for item in output:
        print(item.url)

asyncio.run(main())
```
