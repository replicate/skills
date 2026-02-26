# Replicate in Cloudflare Workflows

Use Cloudflare Workflows to orchestrate multi-step Replicate pipelines with automatic retries and state persistence. Each Replicate API call goes in its own `step.do()` — if it fails, only that step retries, not the whole pipeline.

## Setup

**Install dependencies:**

```
npm install replicate wrangler
```

**`wrangler.jsonc`** — bind the workflow and enable `nodejs_compat`:

```jsonc
{
  "name": "my-replicate-workflow",
  "main": "src/index.js",
  "compatibility_date": "2025-01-01",
  "compatibility_flags": ["nodejs_compat"],
  "workflows": [
    { "name": "replicate-pipeline", "binding": "PIPELINE", "class_name": "ReplicatePipeline" }
  ]
}
```

**Set your API token as a secret:**

```
npx wrangler secret put REPLICATE_API_TOKEN
```

For local dev: `npx wrangler dev --var REPLICATE_API_TOKEN:r8_...`

## Video pipeline: keyframes → interpolation → stitching

Generate three keyframe images in parallel with Flux 2 Klein, feed consecutive pairs as start/end frames to Wan 2.2 I2V to create video segments in parallel, then stitch the segments into a single video.

The Worker's `fetch` handler triggers the workflow. The workflow class contains the durable pipeline logic.

```javascript
// workflow.js
import { WorkflowEntrypoint } from "cloudflare:workers";
import Replicate from "replicate";

export class ReplicatePipeline extends WorkflowEntrypoint {
  async run(event, step) {
    const replicate = new Replicate({ auth: this.env.REPLICATE_API_TOKEN });
    const prompts = event.payload.prompts;

    // Step 1: Generate three keyframe images in parallel.
    // Each step.do is independently retriable — if one keyframe fails,
    // the others don't re-run.
    const keyframes = await Promise.all(
      prompts.map((prompt, i) =>
        step.do(`keyframe-${i}`, { retries: { limit: 3, delay: "5 seconds", backoff: "exponential" } }, async () => {
          const output = await replicate.run("black-forest-labs/flux-2-klein-9b", {
            input: { prompt, aspect_ratio: "16:9" },
          });
          return output.url();
        }),
      ),
    );

    // Step 2: Generate video segments between consecutive keyframes in parallel.
    // keyframes[0]→[1] and keyframes[1]→[2] run at the same time.
    const segments = await Promise.all(
      keyframes.slice(0, -1).map((startFrame, i) =>
        step.do(`video-segment-${i}`, { retries: { limit: 3, delay: "10 seconds", backoff: "exponential" }, timeout: "10 minutes" }, async () => {
          const output = await replicate.run("wan-video/wan-2.2-i2v-fast", {
            input: {
              prompt: prompts[i],
              image: startFrame,
              last_image: keyframes[i + 1],
              num_frames: 81,
            },
          });
          return output.url();
        }),
      ),
    );

    // Step 3: Stitch the video segments into a single continuous video.
    const stitched = await step.do("stitch-videos", { retries: { limit: 3, delay: "10 seconds", backoff: "exponential" }, timeout: "5 minutes" }, async () => {
      const output = await replicate.run(
        "andreasjansson/video-stitcher:11365b52712fbf76932e83bfef43a7ccb1af898fbefcd3da00ecea25d2a40f5e",
        { input: { videos: segments, overlap_seconds: 0.5 } },
      );
      return output.url();
    });

    return { keyframes, segments, stitched };
  }
}

export default {
  async fetch(request, env) {
    const instance = await env.PIPELINE.create({
      params: {
        prompts: [
          "a serene mountain lake at sunrise, cinematic",
          "the sun rising higher over the mountain lake, golden light",
          "bright midday sun over the mountain lake, vivid colors",
        ],
      },
    });

    return Response.json({ id: instance.id, status: "started" });
  },
};
```
