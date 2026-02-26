# Replicate in Cloudflare Workers

Run Replicate models from Cloudflare Workers using the `replicate` npm package. Workers provide sub-millisecond cold starts and a global edge network — pair them with Replicate for AI inference without managing GPU infrastructure.

## Setup

**Install dependencies:**

```
npm install replicate wrangler
```

**Set `nodejs_compat`** in `wrangler.jsonc` — the `replicate` package needs it:

```jsonc
{
  "name": "my-replicate-worker",
  "main": "src/index.js",
  "compatibility_date": "2025-01-01",
  "compatibility_flags": ["nodejs_compat"]
}
```

**Set your API token as a secret** (never put it in code or config):

```
npx wrangler secret put REPLICATE_API_TOKEN
```

For local dev, pass it as a var: `npx wrangler dev --var REPLICATE_API_TOKEN:r8_...`

## Basic prediction

A Worker that generates an image with Pruna P-Image and returns the output URL.

```javascript
// worker.js
import Replicate from "replicate";

export default {
  async fetch(request, env) {
    const replicate = new Replicate({ auth: env.REPLICATE_API_TOKEN });
    const output = await replicate.run("prunaai/p-image", {
      input: { prompt: "a red panda in a bamboo forest" },
    });
    return Response.json({ url: output.url() });
  },
};
```

## Async create + poll

For long-running models, create the prediction and poll for completion. This avoids the 60-second sync timeout.

```javascript
// worker.js
import Replicate from "replicate";

export default {
  async fetch(request, env) {
    const replicate = new Replicate({ auth: env.REPLICATE_API_TOKEN });

    let prediction = await replicate.predictions.create({
      model: "black-forest-labs/flux-2-klein-9b",
      input: { prompt: "a red panda in a bamboo forest", aspect_ratio: "16:9" },
    });

    while (!["succeeded", "failed", "canceled"].includes(prediction.status)) {
      await new Promise((r) => setTimeout(r, 1000));
      prediction = await replicate.predictions.get(prediction.id);
    }

    return Response.json({
      id: prediction.id,
      status: prediction.status,
      output: prediction.output,
    });
  },
};
```

## Concurrent predictions

Fire off multiple predictions in parallel. Workers handle concurrent `fetch` calls well.

```javascript
// worker.js
import Replicate from "replicate";

export default {
  async fetch(request, env) {
    const replicate = new Replicate({ auth: env.REPLICATE_API_TOKEN });

    const prompts = [
      "a red panda eating bamboo",
      "a blue parrot riding a bicycle",
      "a green iguana playing chess",
    ];

    const outputs = await Promise.all(
      prompts.map((prompt) =>
        replicate.run("black-forest-labs/flux-2-klein-9b", {
          input: { prompt, num_outputs: 1 },
        }),
      ),
    );

    const urls = outputs.map((output) => output[0].url);
    return Response.json({ urls });
  },
};
```

## Image editing with user input

Accept a raw image POST and transform it using Qwen Image Edit. The request body is the image bytes — pass them to the model as a `Blob`.

```javascript
// worker.js
import Replicate from "replicate";

export default {
  async fetch(request, env) {
    const replicate = new Replicate({ auth: env.REPLICATE_API_TOKEN });
    const image = await request.blob();

    const output = await replicate.run("qwen/qwen-image-edit-plus", {
      input: {
        image: [image],
        prompt: "Turn this image into lego",
        aspect_ratio: "match_input_image",
        output_format: "webp",
        output_quality: 95,
      },
    });

    return Response.json({ url: output[0].url() });
  },
};
```

## Routing by path

A single Worker that handles different model tasks based on the URL path.

```javascript
// worker.js
import Replicate from "replicate";

export default {
  async fetch(request, env) {
    const replicate = new Replicate({ auth: env.REPLICATE_API_TOKEN });
    const url = new URL(request.url);

    if (url.pathname === "/generate" && request.method === "POST") {
      const body = await request.json();
      const output = await replicate.run("prunaai/p-image", {
        input: { prompt: body.prompt },
      });
      return Response.json({ url: output.url() });
    }

    if (url.pathname === "/caption" && request.method === "POST") {
      const body = await request.json();
      const output = await replicate.run(
        "andreasjansson/blip-2:f677695e5e89f8b236e52ecd1d3f01beb44c34606419bcc19345e046d8f786f9",
        { input: { image: body.image_url, question: "What is in this image?" } },
      );
      return Response.json({ caption: output });
    }

    return Response.json(
      { error: "not found" },
      { status: 404 },
    );
  },
};
```
