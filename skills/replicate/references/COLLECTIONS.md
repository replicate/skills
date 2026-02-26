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

| Slug | Name | Description |
|------|------|-------------|
| `official` | Official AI models | Always available, stable, and predictably priced |
| `text-to-image` | Generate images | Generate images and photos |
| `text-to-video` | Generate videos | Generate videos |
| `image-to-video` | Generate videos from images | Generate videos from images |
| `video-editing` | Edit your videos | Edit your videos |
| `ai-enhance-videos` | Enhance videos | Enhance videos |
| `video-to-text` | Caption videos | Caption videos |
| `image-editing` | Edit any image | Edit any image |
| `super-resolution` | Upscale images with super resolution | Upscale images |
| `ai-image-restoration` | Restore images | Restore images |
| `remove-backgrounds` | Remove backgrounds | Remove backgrounds from images and videos |
| `sketch-to-image` | Turn sketches into images | Transform rough sketches into polished visuals |
| `ai-face-generator` | Generate images from a face | Generate images from a face |
| `face-swap` | Create realistic face swaps | Replace faces across images |
| `generate-anime` | Generate anime-style images and videos | Create anime-style content |
| `generate-emoji` | Generate emojis | Generate custom emojis from text or images |
| `control-net` | Control image generation | Control image generation |
| `language-models` | Large Language Models (LLMs) | Chat, generation, and NLP tasks |
| `vision-models` | Vision models | Image understanding, captioning, and detection |
| `text-to-speech` | Generate speech | Text-to-speech and voice cloning |
| `speech-to-text` | Transcribe speech to text | Transcribe speech to text |
| `ai-music-generation` | Generate music | Generate music |
| `sing-with-voices` | Create songs with voice cloning | Create songs with voice cloning |
| `lipsync` | Lipsync videos | Generate lipsync videos |
| `speaker-diarization` | Speaker diarization | Identify speakers from audio and video |
| `text-recognition-ocr` | OCR to extract text from images | Optical character recognition |
| `text-classification` | Classify text | Classify text by sentiment, topic, intent, or safety |
| `ai-detect-objects` | Object detection and segmentation | Detect and segment objects in images and video |
| `detect-nsfw-content` | Detect NSFW content | Detect NSFW content in images and text |
| `embedding-models` | Embedding models | Embedding models for search and analysis |
| `3d-models` | Create 3D content | Create 3D content |
| `utilities` | Media utilities | Auto-caption, watermark, frame extraction, and more |
| `flux` | FLUX family of models | FLUX image generation and editing models |
| `flux-fine-tunes` | Flux fine-tunes | Community-trained FLUX fine-tunes |
| `flux-kontext-fine-tunes` | Kontext fine-tunes | Custom Kontext image models |
| `qwen-image-fine-tunes` | Qwen-Image fine-tunes | Community-trained Qwen image fine-tunes |
| `wan-video` | WAN family of models | WAN image-to-video and text-to-video models |
| `try-for-free` | Try AI models for free | Free-tier models for video, image, upscaling, and restoration |

The search API also returns matching collections alongside model results.
