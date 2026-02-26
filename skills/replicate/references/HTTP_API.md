# HTTP API Reference

## Authentication

All requests require a Bearer token in the `Authorization` header.

```
Authorization: Bearer r8_your_token_here
```

Get tokens at <https://replicate.com/account/api-tokens>.

## Base URL

```
https://api.replicate.com/v1
```

## Endpoints

### Search

```
GET /v1/search?query={query}
```

Returns matching models, collections, and docs. Each model result includes metadata like `tags`, `generated_description`, and `run_count`. The search API is in beta.

### Collections

```
GET /v1/collections
GET /v1/collections/{collection_slug}
```

List all curated collections, or get one by slug with its models.

### Models

```
GET /v1/models/{owner}/{name}
GET /v1/models/{owner}/{name}/versions
GET /v1/models/{owner}/{name}/versions/{version_id}
GET /v1/models/{owner}/{name}/readme
GET /v1/models/{owner}/{name}/examples
```

The model response includes `latest_version.openapi_schema` with full input/output schemas.

### Predictions

```
POST /v1/predictions                                          # Works for all models
POST /v1/models/{owner}/{name}/predictions                    # Official models only
POST /v1/deployments/{owner}/{name}/predictions               # Deployments only
GET  /v1/predictions/{id}                                     # Poll for result
POST /v1/predictions/{id}/cancel                              # Cancel a running prediction
GET  /v1/predictions                                          # List your predictions
```

The unified `POST /v1/predictions` endpoint accepts these `version` formats:
- `owner/name` — official models (e.g. `black-forest-labs/flux-2-klein-9b`)
- `owner/name:version_id` — community models with pinned version
- `version_id` — raw 64-character version hash

### Deployments

```
GET    /v1/deployments
POST   /v1/deployments
GET    /v1/deployments/{owner}/{name}
PATCH  /v1/deployments/{owner}/{name}
DELETE /v1/deployments/{owner}/{name}
POST   /v1/deployments/{owner}/{name}/predictions
```

### Other

```
GET  /v1/account                  # Current user info
GET  /v1/hardware                 # Available hardware options
POST /v1/files                    # Upload a file
GET  /v1/files/{id}               # Get file metadata
DELETE /v1/files/{id}             # Delete a file
```

## Request/response format

### Creating a prediction

Request:

```json
{
  "version": "black-forest-labs/flux-2-klein-9b",
  "input": {
    "prompt": "a cat wearing a top hat"
  },
  "webhook": "https://example.com/webhook",
  "webhook_events_filter": ["completed"],
  "lifetime": "5m"
}
```

Response:

```json
{
  "id": "gm3qorzdhgbfurvjtvhg6dckhu",
  "model": "black-forest-labs/flux-2-klein-9b",
  "version": "...",
  "input": {"prompt": "a cat wearing a top hat"},
  "output": null,
  "error": null,
  "logs": "",
  "status": "starting",
  "created_at": "2024-01-01T00:00:00.000Z",
  "started_at": null,
  "completed_at": null,
  "metrics": {},
  "urls": {
    "get": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu",
    "cancel": "https://api.replicate.com/v1/predictions/gm3qorzdhgbfurvjtvhg6dckhu/cancel",
    "web": "https://replicate.com/p/gm3qorzdhgbfurvjtvhg6dckhu"
  }
}
```

### Prediction statuses

- `starting` — booting up (may take seconds for warm models, minutes for cold)
- `processing` — model is running
- `succeeded` — done, `output` is populated
- `failed` — error occurred, `error` is populated
- `canceled` — canceled by the user

## Sync mode with `Prefer: wait`

Set the `Prefer` header to hold the connection open until the prediction finishes:

```
Prefer: wait=60
```

The value is seconds (1–60). If the model doesn't finish in time, the response returns the prediction in its current state. Poll `urls.get` to get the final result.

The Python SDK uses sync mode by default with `replicate.run()` (60-second timeout). Pass `wait=False` to disable it.

## Webhooks

Set `webhook` to an HTTPS URL when creating a prediction. Replicate POSTs the full prediction object when it reaches a terminal state.

Filter events with `webhook_events_filter`: `["start", "output", "logs", "completed"]`.

Validate webhook signatures using the `Webhook-ID`, `Webhook-Timestamp`, and `Webhook-Signature` headers. Get your webhook secret from `GET /v1/webhooks/default/secret`.

## Prediction lifetime (auto-cancel)

Set `lifetime` to auto-cancel predictions that run too long:

```json
{"lifetime": "5m"}
```

Accepts durations like `30s`, `5m`, `1h`, `1h30m45s`. Measured from creation time.

## Streaming (SSE)

Models that support streaming include a `stream` URL in the response. Connect to it as an SSE `EventSource` to receive incremental output. Language models typically support streaming.

## Pagination

List endpoints return paginated responses with `next`, `previous`, and `results` fields. Follow the `next` URL to get the next page. The `results` array contains up to 100 items.

## Error responses

Errors return JSON with `title`, `detail`, and `status`:

```json
{
  "title": "Not Found",
  "detail": "Model not found: foo/bar",
  "status": 404
}
```

## Content negotiation

Set `Accept: text/markdown` when fetching Replicate docs pages (e.g. `https://replicate.com/docs`) to get Markdown instead of HTML.

## Output file URLs

File outputs are served from `replicate.delivery` and its subdomains. Add `*.replicate.delivery` to your domain allow list.

Output file URLs expire after 1 hour by default. Save a copy of any files you need to keep.
