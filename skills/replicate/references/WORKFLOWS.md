# Multi-Model Workflows

Complex tasks often require chaining multiple models together. The core pattern is always the same: run models in parallel where possible, pass outputs as inputs to the next step, and stitch results together.

## Core pattern: parallel predictions

Don't wait for one prediction to finish before starting the next. Start all predictions you can, then collect results.

```python
import replicate
import time

pred_a = replicate.predictions.create(
    model="black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a sunrise over mountains"},
)
pred_b = replicate.predictions.create(
    model="black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a sunset over mountains"},
)

def wait(pred_id):
    while True:
        p = replicate.predictions.get(pred_id)
        if p.status in ("succeeded", "failed", "canceled"):
            return p
        time.sleep(1)

result_a, result_b = wait(pred_a.id), wait(pred_b.id)
print(result_a.output)
print(result_b.output)
```

```javascript
const Replicate = require("replicate");
const replicate = new Replicate();

const [predA, predB] = await Promise.all([
  replicate.predictions.create({
    model: "black-forest-labs/flux-2-klein-9b",
    input: { prompt: "a sunrise over mountains" },
  }),
  replicate.predictions.create({
    model: "black-forest-labs/flux-2-klein-9b",
    input: { prompt: "a sunset over mountains" },
  }),
]);

const poll = async (id) => {
  let pred = await replicate.predictions.get(id);
  while (!["succeeded", "failed", "canceled"].includes(pred.status)) {
    await new Promise((r) => setTimeout(r, 1000));
    pred = await replicate.predictions.get(id);
  }
  return pred;
};

const [resultA, resultB] = await Promise.all([poll(predA.id), poll(predB.id)]);
console.log(resultA.output);
console.log(resultB.output);
```

## Pass outputs as inputs

Model output URLs can be passed directly as file inputs to the next model. They're valid for 1 hour.

```python
import replicate

image_output = replicate.run(
    "black-forest-labs/flux-2-klein-9b",
    input={"prompt": "a serene mountain lake at dawn"},
)
image_url = image_output[0].url

caption_output = replicate.run(
    "andreasjansson/blip-2:f677695e5e89f8b236e52ecd1d3f01beb44c34606419bcc19345e046d8f786f9",
    input={"image": image_url, "question": "What is in this image?"},
)
print(caption_output)
```

## Pattern: video generation pipeline

To generate a video from a description:
1. Generate keyframe images with an image model (run in parallel)
2. Generate video clips between keyframes with a video model (run in parallel)
3. Stitch clips together

The exact models depend on the task. Search for the latest video generation models before starting.

## Pattern: image editing pipeline

Edit an image in multiple steps — remove background, apply style, upscale:

```python
import replicate

source_image = "https://picsum.photos/id/237/200/300.jpg"

styled_output = replicate.run(
    "black-forest-labs/flux-kontext-pro",
    input={
        "prompt": "make it look like a watercolor painting",
        "input_image": source_image,
    },
)
print("Styled image:", styled_output.url)
```

## Pattern: audio/video translation

Translate a video's speech to another language:
1. Transcribe speech to text with a speech recognition model
2. Translate the text (using your own LLM capabilities — no model call needed)
3. Generate speech in the target language
4. Lip-sync the new audio to the original video

## Pattern: document extraction

For PDFs or documents, use OCR to extract text, then use your own language model to process it. There's no need to run an LLM on Replicate for text processing — you're already running in one.


