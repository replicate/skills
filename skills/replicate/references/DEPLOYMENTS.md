# Deployments

A deployment is an always-on, private instance of a model version. You configure the hardware, minimum and maximum number of instances, and get a fixed API endpoint. You pay for the uptime of the instances (not per-prediction).

Use deployments when:
- A community model cold-boots too slowly for your use case
- You need a private, stable endpoint for a specific model version
- You want custom scaling (e.g. always keep 2 workers warm)

Official models are already always-warm — you don't need deployments for them.

## Create a deployment

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-deployment",
    "model": "black-forest-labs/flux-dev",
    "version": "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
    "hardware": "gpu-a40-large",
    "min_instances": 1,
    "max_instances": 5
  }' \
  https://api.replicate.com/v1/deployments
```

```python
import replicate

deployment = replicate.deployments.create(
    name="my-deployment",
    model="black-forest-labs/flux-dev",
    version="5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
    hardware="gpu-a40-large",
    min_instances=1,
    max_instances=5,
)
print(deployment.name)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const deployment = await replicate.deployments.create({
  name: "my-deployment",
  model: "black-forest-labs/flux-dev",
  version:
    "5c7d5dc6dd8bf75c1acaa8565735e7986bc5b66206b55cca93cb72c9bf15ccaa",
  hardware: "gpu-a40-large",
  min_instances: 1,
  max_instances: 5,
});
console.log(deployment.name);
```

## List deployments

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/deployments | jq '[.results[] | {name: .name}]'
```

```python
import replicate

page = replicate.deployments.list()
for d in page.results:
    print(d.name)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const page = await replicate.deployments.list();
for (const d of page.results) {
  console.log(d.name);
}
```

## Get a deployment

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/deployments/your-org/my-deployment | jq '{name}'
```

```python
import replicate

deployment = replicate.deployments.get("your-org/my-deployment")
print(deployment.name)
print(deployment.current_release)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const deployment = await replicate.deployments.get("your-org/my-deployment");
console.log(deployment.name);
console.log(deployment.current_release);
```

## Update a deployment

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"min_instances": 2, "max_instances": 10}' \
  https://api.replicate.com/v1/deployments/your-org/my-deployment
```

```python
import replicate

deployment = replicate.deployments.update(
    "your-org",
    "my-deployment",
    min_instances=2,
    max_instances=10,
)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const deployment = await replicate.deployments.update("your-org/my-deployment", {
  min_instances: 2,
  max_instances: 10,
});
```

## Run a prediction against a deployment

Use the deployments predictions endpoint instead of the regular predictions endpoint:

```bash
curl -s -X POST \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait=60" \
  -d '{"input": {"prompt": "a red panda in a bamboo forest"}}' \
  https://api.replicate.com/v1/deployments/your-org/my-deployment/predictions
```

```python
import replicate

deployment = replicate.deployments.get("your-org/my-deployment")
prediction = deployment.predictions.create(
    input={"prompt": "a red panda in a bamboo forest"},
)
print(prediction.id, prediction.status)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const prediction = await replicate.deployments.predictions.create(
  "your-org",
  "my-deployment",
  { input: { prompt: "a red panda in a bamboo forest" } },
);
console.log(prediction.id, prediction.status);
```

## Available hardware

Get available hardware options from the hardware endpoint:

```bash
curl -s -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/hardware | jq '[.[] | {name, sku}]'
```

## Delete a deployment

```bash
curl -s -X DELETE \
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  https://api.replicate.com/v1/deployments/your-org/my-deployment
```

```python
import replicate

replicate.deployments.delete("your-org", "my-deployment")
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

await replicate.deployments.delete("your-org/my-deployment");
```
