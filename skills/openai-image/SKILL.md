---
name: openai-image
version: 1.1.0
description: Generate, edit, describe, restyle, restore, thumbnail, and batch-process images using the OpenAI Images API and GPT-4o vision. Use this skill whenever the user asks to generate, create, make, draw, or design an image or picture using AI, or wants to edit, modify, transform, restyle, composite, or inpaint an existing image. Also handles image description and alt-text generation, background removal, style transfer, photo restoration, thumbnail creation, and batch generation from JSON manifests. Trigger when the user mentions DALL-E, gpt-image, OpenAI image generation, or wants AI-generated visuals for any purpose (logos, mockups, illustrations, thumbnails, icons, concept art, memes). Also trigger for batch image generation, generating a set or series of images, processing multiple images from a manifest, or creating consistent image collections. If the user says "make me an image of...", "generate a picture", "edit this photo to...", "describe this image", "remove the background", "make this look like watercolor", "restore this old photo", "create a thumbnail", "generate a batch of images", or "process this image manifest", this is the skill to use.
---

# OpenAI Image Generation & Editing

Generate images from text prompts, edit existing images, analyze with vision, and apply editorial transforms. Default model is gpt-image-1.5 (fastest, cheapest, best text rendering).

## Quick Start

1. Confirm `OPENAI_API_KEY` is set:
   ```bash
   echo $OPENAI_API_KEY | head -c 10
   ```
2. Install the SDK if needed:
   ```bash
   pip install openai
   ```
3. Generate an image:
   ```bash
   python3 scripts/openai_image.py generate "A watercolor painting of a sunset over Mos Eisley" --output sunset.png
   ```

## Commands

### Generate

Create images from a text prompt.

```bash
# Basic generation
python3 scripts/openai_image.py generate "your prompt" --output result.png

# High quality, specific size
python3 scripts/openai_image.py generate "your prompt" --quality high --size 1536x1024 -o landscape.png

# Transparent background (PNG only)
python3 scripts/openai_image.py generate "a logo on transparent background" --background transparent -o logo.png

# Multiple images at once
python3 scripts/openai_image.py generate "your prompt" -n 4 --output-dir ./variants/

# Compressed JPEG output
python3 scripts/openai_image.py generate "your prompt" --format jpeg --compression 80 -o photo.jpg

# Use the older model if needed
python3 scripts/openai_image.py generate "your prompt" --model gpt-image-1 -o result.png
```

### Edit

Modify existing images with a text prompt. Optionally supply a mask to constrain edits.

```bash
# Edit a single image
python3 scripts/openai_image.py edit "make the sky dramatic and stormy" -i photo.jpg -o dramatic.png

# Edit with a mask (transparent areas in the mask = regions to change)
python3 scripts/openai_image.py edit "replace with a garden" -i room.jpg --mask mask.png -o garden_room.png

# Combine multiple images
python3 scripts/openai_image.py edit "merge these into a collage with consistent lighting" -i img1.jpg img2.jpg img3.jpg -o collage.png

# High input fidelity (preserves more of the original style)
python3 scripts/openai_image.py edit "add a hat" -i portrait.jpg --input-fidelity high -o hat.png
```

#### When to Use Input Fidelity

The `--input-fidelity` flag controls how much the output preserves the source image's structure:

- **Use `high`** when you want to preserve the spatial layout of the source: walls, windows, furniture placement, body poses. Good for stylizing a venue photo while keeping the architecture intact, or retouching a portrait without changing the pose.
- **Omit it (or use `low`)** when the source is a loose reference: you want the AI to use the shape or composition as a starting point but reimagine the contents freely. Good for filling an empty glass with a different liquid, or using a product shot as a structural anchor.

Rule of thumb: if the edit prompt describes *changing what's in the image*, omit fidelity. If it describes *changing how the image looks*, use `high`.

#### Reference-Based Generation

The most powerful edit pattern is using a photo as a **structural anchor** while completely reimagining its contents. Feed a product photo to `edit` not to modify the product, but to let the AI use its shape and proportions as a scaffold for something new.

```bash
# Use an empty coupe glass photo as a structural reference, reimagine the contents
python3 scripts/openai_image.py edit \
  "Fill this coupe glass with a bright blue butterfly pea tea cocktail, violet-shifting ice cubes, condensation on the glass" \
  -i ref_empty_coupe.jpg --quality high -o cocktail_blue.png

# Use a rocks glass photo as a shape anchor for a completely different drink
python3 scripts/openai_image.py edit \
  "Golden amber old fashioned with a large ice sphere, orange peel garnish, smoke wisps" \
  -i ref_rocks_glass.jpg --quality high -o cocktail_amber.png

# Use a venue photo as a layout reference for a different setting
python3 scripts/openai_image.py edit \
  "Transform this space into a 1920s speakeasy with warm Edison bulbs, dark wood, and brass fixtures" \
  -i venue_photo.jpg --input-fidelity high -o speakeasy.png
```

Notice: the first two examples omit `--input-fidelity` because the glass shape is a loose reference. The third uses `--input-fidelity high` because the wall/window layout should be preserved.

### Describe

Analyze images using GPT-4o vision. Returns alt text, captions, tags, or structured analysis.

```bash
# Generate alt text for web accessibility (default)
python3 scripts/openai_image.py describe photo.jpg

# Get a natural language caption
python3 scripts/openai_image.py describe photo.jpg --mode caption

# Detailed multi-paragraph description
python3 scripts/openai_image.py describe photo.jpg --mode detailed

# Keyword tags
python3 scripts/openai_image.py describe photo.jpg --mode tags

# Structured JSON (alt_text, caption, tags, colors, objects, scene)
python3 scripts/openai_image.py describe photo.jpg --mode json

# Custom analysis
python3 scripts/openai_image.py describe photo.jpg --custom "what fonts and colors are used in this design?"

# Multiple images
python3 scripts/openai_image.py describe img1.jpg img2.png img3.webp

# Use the full gpt-4o model for better accuracy
python3 scripts/openai_image.py describe photo.jpg --model gpt-4o
```

### Background Remove

Remove background to transparent PNG.

```bash
python3 scripts/openai_image.py bg-remove product.jpg -o product-nobg.png
```

### Style Transfer

Apply an art style to an image. 10 built-in presets plus custom.

```bash
# Built-in styles: watercolor, oil-painting, pixel-art, pencil-sketch,
#   anime, pop-art, art-deco, minimalist, cyberpunk, stained-glass
python3 scripts/openai_image.py style-transfer photo.jpg --style watercolor -o watercolor.png
python3 scripts/openai_image.py style-transfer photo.jpg --style pixel-art -o pixel.png

# Custom style
python3 scripts/openai_image.py style-transfer photo.jpg --style custom --custom-style "1920s art nouveau poster" -o nouveau.png
```

### Restore

Restore damaged, faded, or degraded photographs. Uses high input fidelity by default.

```bash
python3 scripts/openai_image.py restore old_photo.jpg -o restored.png
```

### Thumbnail

Generate web-optimized thumbnails (JPEG at 80% compression by default).

```bash
# From a text prompt
python3 scripts/openai_image.py thumbnail "a cozy coffee shop interior" -o thumb.jpg

# From an existing image
python3 scripts/openai_image.py thumbnail "clean product shot" --from-image product.jpg -o thumb.jpg
```

### Batch

Process multiple image jobs from a JSON manifest. Each job can generate or edit independently, sharing a common style prefix and defaults.

```bash
python3 scripts/openai_image.py --retries 3 batch drinks.json --output-dir ./public/images/
```

Manifest format (`drinks.json`):
```json
{
  "style_prefix": "Vivid, hyper-real 1920s cinematic movie still. Rich jewel tones, warm golden lighting, film grain.",
  "defaults": {
    "quality": "high",
    "size": "1024x1024",
    "model": "gpt-image-1.5",
    "format": "png"
  },
  "jobs": [
    {
      "name": "cold_open",
      "input": "ref_coupe.jpg",
      "prompt": "Blue butterfly pea tea cocktail with violet-shifting ice cubes, condensation on glass",
      "output": "drink_cold_open.png"
    },
    {
      "name": "smoking_gun",
      "input": "ref_rocks.jpg",
      "prompt": "Golden amber with smoke cloche, large ice sphere, orange peel",
      "output": "drink_smoking_gun.png"
    },
    {
      "name": "hero_banner",
      "prompt": "Elegant bar counter with three cocktails backlit by warm Edison bulbs",
      "output": "hero_banner.png",
      "size": "1536x1024"
    }
  ]
}
```

Each job inherits from `defaults` and can override any field. Jobs with `input` use the edit API (reference-based generation); jobs without `input` use generate. The `style_prefix` is prepended to every job's prompt.

Output is a summary JSON with per-job status:
```json
{
  "status": "success",
  "message": "Batch complete: 3/3 succeeded",
  "results": [
    {"name": "cold_open", "status": "success", "path": "/abs/path/drink_cold_open.png"},
    {"name": "smoking_gun", "status": "success", "path": "/abs/path/drink_smoking_gun.png"},
    {"name": "hero_banner", "status": "success", "path": "/abs/path/hero_banner.png"}
  ]
}
```

## Parameters Reference

### Global flags

These flags go *before* the subcommand name:

| Flag | Values | Default | Notes |
|------|--------|---------|-------|
| `--retries` | `0`-`10` | `0` | Retry transient API errors with exponential backoff (1s, 2s, 4s... capped at 30s) |
| `--prefix` | string | none | Style preamble prepended to prompts in generate, edit, and style-transfer |

```bash
# Example: retry up to 3 times with a style prefix
python3 scripts/openai_image.py --retries 3 --prefix "Photorealistic, 8K, shallow depth of field." generate "a cup of coffee" -o coffee.png
```

### Generation & Editing flags

| Flag | Values | Default | Notes |
|------|--------|---------|-------|
| `--model` | `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`, `dall-e-3` | `gpt-image-1.5` | 1.5 is newest and recommended; mini is cheapest. DALL-E 3 is deprecated (shutdown 2026-05-12). |
| `--size` | `auto`, `1024x1024`, `1536x1024`, `1024x1536` | `auto` | DALL-E 3 also supports `1792x1024`, `1024x1792` |
| `--quality` | `auto`, `low`, `medium`, `high` | `auto` | GPT Image models. DALL-E 3 uses `standard` / `hd` instead. |
| `--format` | `png`, `jpeg`, `webp` | `png` | GPT Image models only; DALL-E returns URL |
| `--compression` | `0`-`100` | none | JPEG/WebP only |
| `--background` | `auto`, `transparent`, `opaque` | `auto` | Transparent requires PNG or WebP format. Best at `medium` or `high` quality. |
| `-n` | `1`-`10` | `1` | Number of images |
| `-o` / `--output` | file path | auto-named | Single image explicit path |
| `--output-dir` | directory | `.` | Where auto-named files go |
| `--input-fidelity` | `low`, `high` | `low` | Edit only. `high` preserves source layout; `low` (default) uses source as loose reference. |

### Describe flags

| Flag | Values | Default | Notes |
|------|--------|---------|-------|
| `--mode` | `alt-text`, `caption`, `detailed`, `tags`, `json` | `alt-text` | Output format for vision analysis |
| `--custom` | string | none | Freeform analysis prompt (overrides --mode) |
| `--model` | `gpt-4o`, `gpt-4o-mini` | `gpt-4o-mini` | Vision model; mini is cheaper, 4o is more accurate |

### Style transfer flags

| Flag | Values | Default |
|------|--------|---------|
| `--style` | `watercolor`, `oil-painting`, `pixel-art`, `pencil-sketch`, `anime`, `pop-art`, `art-deco`, `minimalist`, `cyberpunk`, `stained-glass`, `custom` | required |
| `--custom-style` | string | none (required when `--style custom`) |

### Thumbnail flags

| Flag | Values | Default |
|------|--------|---------|
| `--from-image` | file path | none (generates from prompt if omitted) |
| `--format` | `png`, `jpeg`, `webp` | `jpeg` |
| `--compression` | `0`-`100` | `80` |

### Batch flags

| Flag | Values | Default | Notes |
|------|--------|---------|-------|
| `manifest` (positional) | file path | required | Path to JSON manifest |
| `--output-dir` | directory | `.` | Base directory for output files |

Manifest fields: `style_prefix` (string), `defaults` (object with model/quality/size/format/compression/background/input_fidelity), `jobs` (array of objects with name/prompt/input/output and optional per-job overrides).

### Resolution Expectations

Output dimensions vary by model, quality, and `--size`. This table shows what to expect:

| Model | Quality Levels | Available Sizes | Notes |
|-------|---------------|----------------|-------|
| `gpt-image-1.5` | `low`, `medium`, `high`, `auto` | 1024x1024, 1536x1024, 1024x1536, `auto` | State of the art, recommended |
| `gpt-image-1` | `low`, `medium`, `high`, `auto` | 1024x1024, 1536x1024, 1024x1536, `auto` | Previous generation |
| `gpt-image-1-mini` | `low`, `medium`, `high`, `auto` | 1024x1024, 1536x1024, 1024x1536, `auto` | Budget option, all sizes supported |
| `dall-e-3` | `standard`, `hd` | 1024x1024, 1792x1024, 1024x1792 | **Deprecated.** Shutdown 2026-05-12 |
| `dall-e-2` | `standard` | 256x256, 512x512, 1024x1024 | **Deprecated.** Shutdown 2026-05-12 |

When `--size auto` (the default), the API picks the best size for the prompt. For predictable output, set size explicitly. Use `1536x1024` for landscape backgrounds and hero images, `1024x1024` for product shots and thumbnails, `1024x1536` for portrait/mobile.

**Note:** DALL-E 2 and DALL-E 3 are deprecated and will stop working on May 12, 2026. Migrate to `gpt-image-1.5` for new work.

### Cost Guidance

Per-image costs in USD (as of late 2025). Check [OpenAI pricing](https://openai.com/api/pricing/) for current rates.

| Model | Quality | Square (1024x1024) | Landscape/Portrait (1536x) |
|-------|---------|-------------------|--------------------------|
| `gpt-image-1.5` | `low` | $0.009 | $0.013 |
| `gpt-image-1.5` | `medium` | $0.034 | $0.050 |
| `gpt-image-1.5` | `high` | $0.133 | $0.200 |
| `gpt-image-1-mini` | `low` | $0.005 | $0.006 |
| `gpt-image-1-mini` | `medium` | $0.011 | $0.015 |
| `gpt-image-1-mini` | `high` | $0.036 | $0.052 |
| `dall-e-3` (deprecated) | `standard` | $0.040 | $0.080 |
| `dall-e-3` (deprecated) | `hd` | $0.080 | $0.120 |

**Cost-aware usage for agents:**
- **Draft with `low`, ship with `high`.** Use `--quality low` while iterating on prompts ($0.009/image). Switch to `high` only for the final version ($0.133). That is a 15x cost difference.
- **Use `gpt-image-1-mini` for throwaway work.** At $0.005/image (low quality), it is essentially free for drafting, testing prompts, or generating placeholder images.
- **Batch math matters.** A 10-image batch at `gpt-image-1.5` high quality landscape runs $2.00. The same batch at low quality is $0.13. Ask yourself whether every image in the batch needs high quality, or whether some (backgrounds, textures) can use medium or low.
- **Describe is nearly free.** `gpt-4o-mini` vision calls cost fractions of a cent per image. Use `describe --mode json` freely for analysis, alt text, and tagging.
- **Edit costs the same as generate.** Using a reference photo does not add cost but dramatically improves quality. Always prefer edit with a reference photo over blind generation.
- **Avoid DALL-E 3.** It is deprecated (shutdown May 2026), costs 4x more than `gpt-image-1.5` at standard quality, and produces lower-quality results. Use `gpt-image-1.5` for everything.

## Prompt Tips

The GPT image models respond well to detailed, specific prompts. A few things that help:

- **Be specific about style**: "oil painting", "3D render", "pixel art", "watercolor", "photorealistic"
- **Describe composition**: "close-up", "aerial view", "centered", "rule of thirds"
- **Mention lighting**: "golden hour", "dramatic shadows", "soft diffused light"
- **Include context**: "on a white background", "in a forest setting", "floating in space"

For edits, describe the full desired result rather than just the change. "A portrait of a person wearing a red hat in a garden" works better than "add a hat".

## Consistent Series

When generating a cohesive set of images (product shots, menu items, page backgrounds), use these techniques to keep them visually unified:

**1. Use `--prefix` for a shared style preamble.** Every prompt gets the same visual DNA:
```bash
PREFIX="Vivid, hyper-real 1920s cinematic movie still. Rich jewel tones, warm golden lighting, film grain."

python3 scripts/openai_image.py --prefix "$PREFIX" generate "blue cocktail in a coupe glass" --quality high -o drink1.png
python3 scripts/openai_image.py --prefix "$PREFIX" generate "amber old fashioned with smoke" --quality high -o drink2.png
python3 scripts/openai_image.py --prefix "$PREFIX" generate "emerald absinthe drip" --quality high -o drink3.png
```

**2. Use `batch` for manifests.** Define the prefix once, list all jobs:
```bash
python3 scripts/openai_image.py --retries 3 batch drinks.json --output-dir ./public/images/
```

**3. Keep quality and size consistent.** Mixing `--quality medium` and `--quality high` across a series produces visible inconsistency. Pick one and stick with it.

**4. Use reference photos as structural anchors.** Feed the same glass, product, or venue photo into multiple `edit` calls with different prompts. The shared geometry keeps the series grounded. See "Reference-Based Generation" above.

**5. The "Mise en place" method.** When generating images that involve multiple steps, variations, or use the same recurring elements (like ingredients for a recipe, tools for a craft, or parts of a product), first generate a single "mise en place" style image that contains all the individual elements laid out clearly on a flat, neutral surface. You can then use this initial "ingredients" image as a structural anchor (using `edit` with `--input-fidelity`) for subsequent generations, ensuring visual consistency of the core components across the entire series.

## Masks

Masks are PNG files with an alpha channel. Fully transparent pixels mark the area to edit; opaque pixels protect the original. To create a mask:

1. Open the source image in any editor (GIMP, Photoshop, Preview)
2. Erase the region you want to change (make it transparent)
3. Save as PNG (preserves alpha channel)

The mask must match the source image dimensions.

## Output

All commands return structured JSON:

```json
{
  "status": "success",
  "message": "Generated 1 image(s)",
  "model": "gpt-image-1.5",
  "images": [
    {"index": 0, "path": "/absolute/path/to/gen_20260304_143022.png"}
  ]
}
```

The `describe` command returns text instead of images:
```json
{
  "status": "success",
  "message": "Described 1 image",
  "model": "gpt-4o-mini",
  "mode": "alt-text",
  "result": {
    "file": "/path/to/photo.jpg",
    "description": "Pixel art spaceship with blue cockpit and orange thrusters on white background"
  }
}
```

## Troubleshooting

- **"OPENAI_API_KEY not set"**: Run `export OPENAI_API_KEY='sk-...'` or add it to `~/.bashrc`.
- **"openai package is not installed"**: Run `pip install openai`.
- **Billing/quota errors**: Check your OpenAI account at platform.openai.com for usage limits.
- **Mask dimension mismatch**: Resize the mask to match the source image exactly.
- **DALL-E 3 format errors**: DALL-E 3 does not support `--format` or `--background`. Omit those flags or use a GPT image model.
- **Transient API errors (connection, timeout, 502/503)**: The OpenAI Images API has a roughly 10-20% transient failure rate under load. Use `--retries 3` to automatically retry with exponential backoff (1s, 2s, 4s delays). Retry status is logged to stderr so you can monitor progress. For batch jobs, always use `--retries 3`.
- **Empty output file**: The script now verifies every saved file is non-empty. If you see a `WriteError`, the API returned empty data. Retry the command or check your API quota.
