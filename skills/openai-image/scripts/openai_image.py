#!/usr/bin/env python3
"""
OpenAI Images API CLI -- generate, edit, describe, and transform images.

Usage:
    python3 scripts/openai_image.py <command> [options]

Commands:
    generate        Create an image from a text prompt
    edit            Modify an existing image (with optional mask)
    describe        Analyze image(s) with GPT-4o vision
    bg-remove       Remove background to transparent PNG
    style-transfer  Apply an art style to an image
    restore         Restore a damaged/degraded photograph
    thumbnail       Generate or adapt a web-ready thumbnail
    batch           Process multiple jobs from a JSON manifest

Requires: openai (pip install openai)
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import struct
import sys
import time
import traceback
import zlib
from pathlib import Path

# ── Structured output helpers ────────────────────────────────────────

class ImageCLIError(Exception):
    """Raised by helpers when an operation fails. Caught by commands for
    structured JSON output, or by batch for per-job error recording."""
    def __init__(self, message: str, typ: str = "Error", fix: str | None = None):
        super().__init__(message)
        self.typ = typ
        self.fix = fix


def success(data=None):
    if data is None:
        data = {}
    print(json.dumps({"status": "success", **data}, indent=2))
    sys.exit(0)


def error(message: str, typ: str = "Error", fix: str | None = None):
    ret = {"status": "error", "message": message, "type": typ}
    if fix:
        ret["fix"] = fix
    print(json.dumps(ret, indent=2))
    sys.exit(1)


# ── Client init ──────────────────────────────────────────────────────

def get_client():
    try:
        from openai import OpenAI
    except ImportError:
        error(
            "openai package is not installed.",
            "DependencyMissing",
            fix="pip install openai",
        )

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        error(
            "OPENAI_API_KEY environment variable is not set.",
            "AuthError",
            fix="Export your key: export OPENAI_API_KEY='sk-...'",
        )

    return OpenAI(api_key=api_key)


# ── Save helper ──────────────────────────────────────────────────────

def save_image(b64_data: str, output_path: Path, fmt: str) -> Path:
    """Decode base64 image data and write to disk."""
    image_bytes = base64.b64decode(b64_data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(image_bytes)
    return output_path


def default_output_path(prefix: str, fmt: str, index: int, output_dir: Path) -> Path:
    """Generate a timestamped output filename."""
    ts = time.strftime("%Y%m%d_%H%M%S")
    suffix = fmt if fmt != "jpeg" else "jpg"
    name = f"{prefix}_{ts}_{index}.{suffix}" if index > 0 else f"{prefix}_{ts}.{suffix}"
    return output_dir / name


def verify_output(path: Path):
    """Check that a written file exists and has nonzero size. Raises ImageCLIError if not."""
    if not path.exists():
        raise ImageCLIError(f"Output file was not written: {path}", "WriteError")
    if path.stat().st_size == 0:
        path.unlink()
        raise ImageCLIError(f"Output file is empty (0 bytes), deleted: {path}", "WriteError")


def apply_prefix(prompt: str, prefix: str | None) -> str:
    """Prepend a style prefix to a prompt if provided."""
    if not prefix:
        return prompt
    return f"{prefix.rstrip()} {prompt}"


def embed_png_metadata(path: Path, metadata: dict):
    """Write key-value pairs as PNG tEXt chunks before the IEND chunk."""
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return
    iend_idx = data.rfind(b'IEND')
    if iend_idx < 4:
        return
    iend_start = iend_idx - 4  # start of length field
    chunks = b''
    for key, value in metadata.items():
        chunk_data = key.encode('latin-1', errors='replace') + b'\x00' + value.encode('latin-1', errors='replace')
        length = struct.pack('>I', len(chunk_data))
        crc = struct.pack('>I', zlib.crc32(b'tEXt' + chunk_data) & 0xFFFFFFFF)
        chunks += length + b'tEXt' + chunk_data + crc
    path.write_bytes(data[:iend_start] + chunks + data[iend_start:])


def tag_image(path: Path, fmt: str, prompt: str, model: str,
              quality: str = "auto", size: str = "auto"):
    """Embed generation metadata in PNG files. No-op for other formats."""
    if fmt != "png":
        return
    embed_png_metadata(path, {
        "Software": "openai-image-skill",
        "Description": prompt[:500],
        "model": model,
        "quality": quality,
        "size": size,
    })


# ── Retry wrapper ────────────────────────────────────────────────────

def _is_transient(exc):
    """Return True if the exception looks like a transient API/network error."""
    name = type(exc).__name__
    if name in ("APIConnectionError", "APITimeoutError", "InternalServerError",
                "RateLimitError", "ConnectionError", "TimeoutError"):
        return True
    msg = str(exc).lower()
    if any(k in msg for k in ("connection", "timeout", "rate limit", "502", "503", "529")):
        return True
    return False


def api_call_with_retry(fn, retries: int = 0, seekables=None):
    """Call fn(), retrying on transient errors with exponential backoff.

    Args:
        fn: callable that performs the API call
        retries: max retry attempts (0 = no retries)
        seekables: optional list of file-like objects to seek(0) before each retry,
                   preventing exhausted-stream errors when the SDK re-reads the body

    Returns the result of fn(). On permanent errors, raises ImageCLIError.
    """
    last_exc = None
    for attempt in range(1 + retries):
        try:
            return fn()
        except (SystemExit, ImageCLIError):
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < retries and _is_transient(exc):
                wait = min(2 ** attempt, 30)  # cap at 30 seconds
                print(
                    json.dumps({"status": "retry", "attempt": attempt + 1,
                                "max_retries": retries, "wait_seconds": wait,
                                "error": str(exc)}),
                    file=sys.stderr,
                )
                time.sleep(wait)
                # Reset file handles so the next attempt can re-read them
                if seekables:
                    for f in seekables:
                        if hasattr(f, "seek"):
                            f.seek(0)
                continue
            raise ImageCLIError(str(exc), "APIError")
    raise ImageCLIError(str(last_exc), "APIError")


# ── Constants ────────────────────────────────────────────────────────

DESCRIBE_PROMPTS = {
    "alt-text": (
        "Write concise alt text for this image, suitable for a web <img> alt attribute. "
        "One sentence, under 125 characters. No quotes around the output. "
        "Describe the meaningful content, not decorative details."
    ),
    "caption": (
        "Write a single natural-language sentence that captions this image. "
        "Be descriptive but concise. No quotes around the output."
    ),
    "detailed": (
        "Provide a comprehensive multi-paragraph description of this image. "
        "Cover the subject, composition, colors, lighting, mood, notable objects, "
        "text visible in the image, and any other relevant details. "
        "Use plain prose, no bullet points or markdown."
    ),
    "tags": (
        "Return a flat comma-separated list of keyword tags for this image. "
        "Include subject matter, objects, colors, mood, style, and setting. "
        "Lowercase, no hashtags, no numbering. Example: sunset, ocean, orange sky, calm"
    ),
    "json": (
        "Analyze this image and return ONLY valid JSON (no markdown fences) with "
        "these fields:\n"
        '  "alt_text": concise alt text under 125 chars,\n'
        '  "caption": one-sentence natural language caption,\n'
        '  "tags": array of lowercase keyword strings,\n'
        '  "colors": array of dominant hex color strings,\n'
        '  "objects": array of notable objects/subjects detected,\n'
        '  "scene": one-word scene type (indoor, outdoor, abstract, portrait, etc.)\n'
        "Return raw JSON only. No explanation, no markdown."
    ),
}

MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}

STYLE_PRESETS = {
    "watercolor": "a delicate watercolor painting with soft washes, visible paper texture, and gentle color bleeding",
    "oil-painting": "a rich oil painting with visible brushstrokes, deep colors, and painterly texture",
    "pixel-art": "retro pixel art with a limited color palette, clean pixel edges, and a nostalgic 8-bit aesthetic",
    "pencil-sketch": "a detailed pencil sketch with crosshatching, shading gradients, and visible graphite texture on paper",
    "anime": "Japanese anime style with cel shading, vibrant colors, expressive features, and clean linework",
    "pop-art": "bold pop art in the style of Roy Lichtenstein with Ben-Day dots, thick outlines, and saturated primary colors",
    "art-deco": "elegant Art Deco illustration with geometric patterns, gold accents, symmetry, and 1920s glamour",
    "minimalist": "clean minimalist illustration with flat colors, simple shapes, generous whitespace, and reduced detail",
    "cyberpunk": "cyberpunk aesthetic with neon glows, dark urban atmosphere, holographic highlights, and high-tech grit",
    "stained-glass": "stained glass artwork with bold black leading lines, jewel-toned translucent color segments, and luminous backlight",
}

STYLE_CHOICES = list(STYLE_PRESETS.keys()) + ["custom"]

PRESETS = {
    "draft": {"model": "gpt-image-1-mini", "quality": "low"},
    "balanced": {"model": "gpt-image-1.5", "quality": "medium"},
    "final": {"model": "gpt-image-1.5", "quality": "high"},
}

COST_TABLE = {
    "gpt-image-1.5": {
        "low": {"square": 0.009, "rect": 0.013},
        "medium": {"square": 0.034, "rect": 0.050},
        "high": {"square": 0.133, "rect": 0.200},
    },
    "gpt-image-1": {
        "low": {"square": 0.009, "rect": 0.013},
        "medium": {"square": 0.034, "rect": 0.050},
        "high": {"square": 0.133, "rect": 0.200},
    },
    "gpt-image-1-mini": {
        "low": {"square": 0.005, "rect": 0.006},
        "medium": {"square": 0.011, "rect": 0.015},
        "high": {"square": 0.036, "rect": 0.052},
    },
    "dall-e-3": {
        "standard": {"square": 0.040, "rect": 0.080},
        "hd": {"square": 0.080, "rect": 0.120},
    },
}


def estimate_cost(model: str, quality: str, size: str) -> float:
    """Estimate per-image cost in USD. Returns 0.0 for unknown combos."""
    model_costs = COST_TABLE.get(model)
    if not model_costs:
        return 0.0
    q = quality if quality != "auto" else "medium"
    quality_costs = model_costs.get(q)
    if not quality_costs:
        return 0.0
    is_rect = size in ("1536x1024", "1024x1536", "1792x1024", "1024x1792")
    return quality_costs["rect" if is_rect else "square"]


def handle_dry_run(args, items=None):
    """If --dry-run is set, print cost estimate and exit."""
    if not getattr(args, "dry_run", False):
        return
    if items is None:
        n = getattr(args, "n", 1)
        items = [{
            "model": getattr(args, "model", "gpt-image-1.5"),
            "quality": getattr(args, "quality", "auto"),
            "size": getattr(args, "size", "auto"),
            "n": n,
        }]
    breakdown = []
    total = 0.0
    for item in items:
        per_image = estimate_cost(item["model"], item["quality"], item["size"])
        n = item.get("n", 1)
        cost = per_image * n
        total += cost
        entry = {"model": item["model"], "quality": item["quality"],
                 "size": item["size"], "n": n, "cost_usd": round(cost, 4)}
        if "name" in item:
            entry = {"name": item["name"], **entry}
        breakdown.append(entry)
    print(json.dumps({
        "status": "dry_run",
        "estimated_cost_usd": round(total, 4),
        "breakdown": breakdown,
    }, indent=2))
    sys.exit(0)


def apply_preset(args):
    """Apply --preset to model and quality if user didn't explicitly override."""
    preset_name = getattr(args, "preset", None)
    if not preset_name:
        return
    preset = PRESETS[preset_name]
    if getattr(args, "model", "gpt-image-1.5") == "gpt-image-1.5":
        args.model = preset["model"]
    if getattr(args, "quality", "auto") == "auto":
        args.quality = preset["quality"]


# ── Vision helper ────────────────────────────────────────────────────

def encode_image(image_path):
    """Read a local image file and return (base64_string, mime_type)."""
    suffix = image_path.suffix.lower()
    mime = MIME_TYPES.get(suffix)
    if not mime:
        error(
            f"Unsupported image format '{suffix}' for file: {image_path}",
            "UnsupportedFormat",
            fix=f"Supported formats: {', '.join(sorted(MIME_TYPES.keys()))}",
        )
    raw = image_path.read_bytes()
    b64 = base64.b64encode(raw).decode("utf-8")
    return b64, mime


# ── Generate command ─────────────────────────────────────────────────

def command_generate(args):
    handle_dry_run(args)
    client = get_client()
    prompt = apply_prefix(args.prompt, getattr(args, "prefix", None))

    kwargs = {
        "model": args.model,
        "prompt": prompt,
        "n": args.n,
    }

    if args.size != "auto":
        kwargs["size"] = args.size
    if args.quality != "auto":
        kwargs["quality"] = args.quality
    if args.model.startswith("gpt-image"):
        kwargs["output_format"] = args.format
        if args.compression is not None:
            kwargs["output_compression"] = args.compression
        if args.background != "auto":
            kwargs["background"] = args.background

    retries = getattr(args, "retries", 0)
    result = api_call_with_retry(lambda: client.images.generate(**kwargs), retries)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for i, img in enumerate(result.data):
        b64 = img.b64_json
        if b64 is None:
            saved.append({"index": i, "url": img.url})
            continue
        if args.output and args.n == 1:
            out_path = Path(args.output).resolve()
        else:
            out_path = default_output_path("gen", args.format, i, output_dir)
        save_image(b64, out_path, args.format)
        verify_output(out_path)
        tag_image(out_path, args.format, prompt, args.model, args.quality, args.size)
        saved.append({"index": i, "path": str(out_path)})

    success({
        "message": f"Generated {len(saved)} image(s)",
        "model": args.model,
        "images": saved,
    })


# ── Edit command ─────────────────────────────────────────────────────

def command_edit(args):
    handle_dry_run(args)
    client = get_client()
    prompt = apply_prefix(args.prompt, getattr(args, "prefix", None))

    image_paths = [Path(p).resolve() for p in args.image]
    for p in image_paths:
        if not p.exists():
            error(f"Input image not found: {p}", "FileNotFound")

    if len(image_paths) == 1:
        image_arg = open(str(image_paths[0]), "rb")
    else:
        image_arg = [open(str(p), "rb") for p in image_paths]

    kwargs = {
        "model": args.model,
        "image": image_arg,
        "prompt": prompt,
        "n": args.n,
    }

    if args.size != "auto":
        kwargs["size"] = args.size
    if args.quality != "auto":
        kwargs["quality"] = args.quality
    if args.mask:
        mask_path = Path(args.mask).resolve()
        if not mask_path.exists():
            error(f"Mask file not found: {mask_path}", "FileNotFound")
        kwargs["mask"] = open(str(mask_path), "rb")
    if args.model.startswith("gpt-image"):
        kwargs["output_format"] = args.format
        if args.compression is not None:
            kwargs["output_compression"] = args.compression
        if args.background != "auto":
            kwargs["background"] = args.background
        if args.input_fidelity:
            kwargs["input_fidelity"] = args.input_fidelity

    retries = getattr(args, "retries", 0)
    file_handles = (image_arg if isinstance(image_arg, list) else [image_arg])
    if "mask" in kwargs:
        file_handles = file_handles + [kwargs["mask"]]
    try:
        result = api_call_with_retry(lambda: client.images.edit(**kwargs), retries, seekables=file_handles)
    finally:
        if isinstance(image_arg, list):
            for f in image_arg:
                f.close()
        else:
            image_arg.close()
        if "mask" in kwargs and hasattr(kwargs["mask"], "close"):
            kwargs["mask"].close()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for i, img in enumerate(result.data):
        b64 = img.b64_json
        if b64 is None:
            saved.append({"index": i, "url": img.url})
            continue
        if args.output and args.n == 1:
            out_path = Path(args.output).resolve()
        else:
            out_path = default_output_path("edit", args.format, i, output_dir)
        save_image(b64, out_path, args.format)
        verify_output(out_path)
        tag_image(out_path, args.format, prompt, args.model, args.quality, args.size)
        saved.append({"index": i, "path": str(out_path)})

    success({
        "message": f"Edited {len(saved)} image(s)",
        "model": args.model,
        "images": saved,
    })


# ── Describe command (GPT-4o vision) ─────────────────────────────────

def command_describe(args):
    client = get_client()

    image_paths = [Path(p).resolve() for p in args.image]
    for p in image_paths:
        if not p.exists():
            error(f"Input image not found: {p}", "FileNotFound")

    if args.custom:
        prompt_text = args.custom
    else:
        prompt_text = DESCRIBE_PROMPTS[args.mode]

    max_tokens = 300 if (args.mode in ("alt-text", "caption", "tags") and not args.custom) else 1500

    results = []
    for p in image_paths:
        b64_data, mime = encode_image(p)

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_data}"}},
            ],
        }]

        retries = getattr(args, "retries", 0)
        response = api_call_with_retry(
            lambda m=messages: client.chat.completions.create(
                model=args.model, messages=m, max_tokens=max_tokens,
            ),
            retries,
        )

        text = response.choices[0].message.content.strip()

        # For JSON mode, parse into a proper dict for clean output
        if args.mode == "json" and not args.custom:
            try:
                text = json.loads(text)
            except json.JSONDecodeError:
                pass

        results.append({"file": str(p), "description": text})

    if len(results) == 1:
        success({
            "message": "Described 1 image",
            "model": args.model,
            "mode": "custom" if args.custom else args.mode,
            "result": results[0],
        })
    else:
        success({
            "message": f"Described {len(results)} images",
            "model": args.model,
            "mode": "custom" if args.custom else args.mode,
            "results": results,
        })


# ── Background remove command ────────────────────────────────────────

def command_bg_remove(args):
    handle_dry_run(args)
    client = get_client()

    image_path = Path(args.image).resolve()
    if not image_path.exists():
        error(f"Input image not found: {image_path}", "FileNotFound")

    image_file = open(str(image_path), "rb")

    kwargs = {
        "model": args.model,
        "image": image_file,
        "prompt": (
            "Remove the background completely, keeping only the main subject. "
            "Output on a fully transparent background."
        ),
        "n": 1,
        "output_format": "png",
        "background": "transparent",
    }
    if args.quality != "auto":
        kwargs["quality"] = args.quality

    retries = getattr(args, "retries", 0)
    try:
        result = api_call_with_retry(lambda: client.images.edit(**kwargs), retries, seekables=[image_file])
    finally:
        image_file.close()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_path = default_output_path("bg_remove", "png", 0, output_dir)

    b64 = result.data[0].b64_json
    if b64:
        save_image(b64, out_path, "png")
        verify_output(out_path)
        tag_image(out_path, "png", "background removal", args.model, args.quality, "auto")
        success({
            "message": f"Background removed from {image_path.name}",
            "model": args.model,
            "images": [{"index": 0, "path": str(out_path)}],
        })
    else:
        success({
            "message": f"Background removed from {image_path.name}",
            "model": args.model,
            "images": [{"index": 0, "url": result.data[0].url}],
        })


# ── Style transfer command ───────────────────────────────────────────

def command_style_transfer(args):
    handle_dry_run(args)
    client = get_client()

    image_path = Path(args.image).resolve()
    if not image_path.exists():
        error(f"Input image not found: {image_path}", "FileNotFound")

    if args.style == "custom":
        if not args.custom_style:
            error(
                "--custom-style is required when --style is 'custom'.",
                "ArgError",
                fix="Add --custom-style 'your description here'",
            )
        style_desc = args.custom_style
    else:
        style_desc = STYLE_PRESETS[args.style]

    prompt = (
        f"Transform this image into {style_desc} style while preserving "
        "the composition and subject matter."
    )
    prompt = apply_prefix(prompt, getattr(args, "prefix", None))

    image_file = open(str(image_path), "rb")

    kwargs = {
        "model": args.model,
        "image": image_file,
        "prompt": prompt,
        "n": 1,
    }
    if args.size != "auto":
        kwargs["size"] = args.size
    if args.quality != "auto":
        kwargs["quality"] = args.quality
    if args.model.startswith("gpt-image"):
        kwargs["output_format"] = args.format

    retries = getattr(args, "retries", 0)
    try:
        result = api_call_with_retry(lambda: client.images.edit(**kwargs), retries, seekables=[image_file])
    finally:
        image_file.close()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = args.format
    if args.output:
        out_path = Path(args.output).resolve()
    else:
        style_tag = args.style.replace("-", "_")
        out_path = default_output_path(f"style_{style_tag}", fmt, 0, output_dir)

    b64 = result.data[0].b64_json
    if b64:
        save_image(b64, out_path, fmt)
        verify_output(out_path)
        tag_image(out_path, fmt, prompt, args.model, args.quality, args.size)
        success({
            "message": f"Applied {args.style} style to {image_path.name}",
            "model": args.model,
            "style": args.style,
            "images": [{"index": 0, "path": str(out_path)}],
        })
    else:
        success({
            "message": f"Applied {args.style} style to {image_path.name}",
            "model": args.model,
            "style": args.style,
            "images": [{"index": 0, "url": result.data[0].url}],
        })


# ── Restore command ──────────────────────────────────────────────────

def command_restore(args):
    handle_dry_run(args)
    client = get_client()

    image_path = Path(args.image).resolve()
    if not image_path.exists():
        error(f"Input image not found: {image_path}", "FileNotFound")

    image_file = open(str(image_path), "rb")

    kwargs = {
        "model": args.model,
        "image": image_file,
        "prompt": (
            "Restore this damaged, faded, or degraded photograph. Fix any "
            "scratches, tears, discoloration, noise, or blur while preserving "
            "the original content and composition. Make it look like a clean, "
            "well-preserved version of the original."
        ),
        "n": 1,
    }
    if args.size != "auto":
        kwargs["size"] = args.size
    if args.quality != "auto":
        kwargs["quality"] = args.quality
    if args.model.startswith("gpt-image"):
        kwargs["output_format"] = args.format
        kwargs["input_fidelity"] = "high"

    retries = getattr(args, "retries", 0)
    try:
        result = api_call_with_retry(lambda: client.images.edit(**kwargs), retries, seekables=[image_file])
    finally:
        image_file.close()

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = args.format
    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_path = default_output_path("restore", fmt, 0, output_dir)

    b64 = result.data[0].b64_json
    if b64:
        save_image(b64, out_path, fmt)
        verify_output(out_path)
        tag_image(out_path, fmt, "photo restoration", args.model, args.quality, args.size)
        success({
            "message": f"Restored {image_path.name}",
            "model": args.model,
            "images": [{"index": 0, "path": str(out_path)}],
        })
    else:
        success({
            "message": f"Restored {image_path.name}",
            "model": args.model,
            "images": [{"index": 0, "url": result.data[0].url}],
        })


# ── Thumbnail command ────────────────────────────────────────────────

def command_thumbnail(args):
    handle_dry_run(args)
    client = get_client()

    fmt = args.format
    compression = args.compression

    if args.from_image:
        image_path = Path(args.from_image).resolve()
        if not image_path.exists():
            error(f"Input image not found: {image_path}", "FileNotFound")

        prompt = (
            (f"{args.prompt}. " if args.prompt else "") +
            "Optimize this image as a web thumbnail. Ensure the subject is "
            "clearly visible at small sizes, boost contrast slightly, and "
            "sharpen details for crisp rendering at reduced dimensions."
        )

        image_file = open(str(image_path), "rb")
        kwargs = {
            "model": args.model,
            "image": image_file,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        if args.quality != "auto":
            kwargs["quality"] = args.quality
        if args.model.startswith("gpt-image"):
            kwargs["output_format"] = fmt
            if compression is not None:
                kwargs["output_compression"] = compression

        retries = getattr(args, "retries", 0)
        try:
            result = api_call_with_retry(lambda: client.images.edit(**kwargs), retries, seekables=[image_file])
        finally:
            image_file.close()
    else:
        if not args.prompt:
            error(
                "A text prompt is required when not using --from-image.",
                "ArgError",
                fix="Provide a prompt or use --from-image",
            )

        kwargs = {
            "model": args.model,
            "prompt": args.prompt,
            "n": 1,
            "size": "1024x1024",
        }
        if args.quality != "auto":
            kwargs["quality"] = args.quality
        if args.model.startswith("gpt-image"):
            kwargs["output_format"] = fmt
            if compression is not None:
                kwargs["output_compression"] = compression

        retries = getattr(args, "retries", 0)
        result = api_call_with_retry(lambda: client.images.generate(**kwargs), retries)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        out_path = default_output_path("thumb", fmt, 0, output_dir)

    b64 = result.data[0].b64_json
    if b64:
        save_image(b64, out_path, fmt)
        verify_output(out_path)
        tag_image(out_path, fmt, args.prompt or "thumbnail", args.model, args.quality, "1024x1024")
        success({
            "message": f"Thumbnail {'from image' if args.from_image else 'generated'}",
            "model": args.model,
            "format": fmt,
            "compression": compression,
            "images": [{"index": 0, "path": str(out_path)}],
        })
    else:
        success({
            "message": f"Thumbnail {'from image' if args.from_image else 'generated'}",
            "model": args.model,
            "images": [{"index": 0, "url": result.data[0].url}],
        })


def generate_gallery_html(output_dir, results, manifest):
    """Generate an index.html gallery for batch results."""
    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    style_prefix = manifest.get("style_prefix", "")
    jobs = manifest.get("jobs", [])
    job_map = {j.get("name", f"job_{i}"): j for i, j in enumerate(jobs)}
    succeeded = sum(1 for r in results if r.get("status") == "success")

    rows = []
    for r in results:
        name = r.get("name", "")
        job = job_map.get(name, {})
        prompt = job.get("prompt", "")
        path = r.get("path")

        if r.get("status") == "success" and path:
            fname = Path(path).name
            img_tag = f'<img src="{esc(fname)}" alt="{esc(name)}" loading="lazy">'
        else:
            err_msg = r.get("message", "failed")
            img_tag = f'<div class="error">{esc(err_msg)}</div>'

        rows.append(
            f'<div class="card">\n'
            f'  {img_tag}\n'
            f'  <div class="info"><strong>{esc(name)}</strong>'
            f'<p>{esc(prompt)}</p></div>\n'
            f'</div>'
        )

    prefix_note = f' | prefix: {esc(style_prefix[:80])}' if style_prefix else ''
    html = (
        '<!DOCTYPE html>\n<html lang="en"><head>\n'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>Batch Gallery</title>\n<style>\n'
        '  *{margin:0;padding:0;box-sizing:border-box}\n'
        '  body{font-family:system-ui,-apple-system,sans-serif;background:#111;color:#eee;padding:2rem}\n'
        '  h1{margin-bottom:.5rem;font-size:1.5rem}\n'
        '  .meta{color:#888;margin-bottom:2rem;font-size:.9rem}\n'
        '  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.5rem}\n'
        '  .card{background:#1a1a1a;border-radius:8px;overflow:hidden}\n'
        '  .card img{width:100%;height:auto;display:block}\n'
        '  .card .error{padding:3rem 1rem;text-align:center;color:#f87171;background:#1c1c1c}\n'
        '  .info{padding:.75rem 1rem}\n'
        '  .info strong{display:block;margin-bottom:.25rem}\n'
        '  .info p{color:#aaa;font-size:.85rem;line-height:1.4}\n'
        '</style></head><body>\n'
        f'<h1>Batch Gallery</h1>\n'
        f'<p class="meta">{succeeded}/{len(results)} succeeded{prefix_note}</p>\n'
        f'<div class="grid">\n{"".join(rows)}\n</div>\n'
        '</body></html>'
    )

    gallery_path = output_dir / "index.html"
    gallery_path.write_text(html)
    return str(gallery_path)


# ── Batch command ────────────────────────────────────────────────────

def command_batch(args):
    """Process multiple image jobs from a JSON manifest file."""
    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.exists():
        error(f"Manifest file not found: {manifest_path}", "FileNotFound")

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in manifest: {e}", "ManifestError")

    style_prefix = manifest.get("style_prefix", "")
    defaults = manifest.get("defaults", {})
    jobs = manifest.get("jobs", [])
    if not jobs:
        error("Manifest contains no jobs.", "ManifestError")

    # Dry-run: estimate cost without making API calls
    if getattr(args, "dry_run", False):
        dry_items = []
        for idx, job in enumerate(jobs):
            job_name = job.get("name", f"job_{idx}")
            m = job.get("model", defaults.get("model", "gpt-image-1.5"))
            q = job.get("quality", defaults.get("quality", "auto"))
            s = job.get("size", defaults.get("size", "auto"))
            dry_items.append({"name": job_name, "model": m, "quality": q, "size": s, "n": 1})
        handle_dry_run(args, dry_items)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    client = get_client()
    retries = getattr(args, "retries", 0)
    results = []

    total_jobs = len(jobs)
    for idx, job in enumerate(jobs):
        job_name = job.get("name", f"job_{idx}")
        print(f"[{idx + 1}/{total_jobs}] {job_name}...", file=sys.stderr, flush=True)
        raw_prompt = job.get("prompt")
        if not raw_prompt:
            results.append({"name": job_name, "status": "error", "message": "Missing prompt"})
            continue

        prompt = apply_prefix(raw_prompt, style_prefix if style_prefix else None)
        input_path = job.get("input")
        output_name = job.get("output")

        # Merge defaults with per-job overrides
        model = job.get("model", defaults.get("model", "gpt-image-1.5"))
        quality = job.get("quality", defaults.get("quality", "auto"))
        size = job.get("size", defaults.get("size", "auto"))
        fmt = job.get("format", defaults.get("format", "png"))
        compression = job.get("compression", defaults.get("compression"))
        background = job.get("background", defaults.get("background", "auto"))
        input_fidelity = job.get("input_fidelity", defaults.get("input_fidelity"))

        if output_name:
            out_path = output_dir / output_name
        else:
            out_path = default_output_path(f"batch_{job_name}", fmt, 0, output_dir)

        try:
            if input_path:
                # Edit mode
                img_path = Path(input_path).resolve()
                if not img_path.exists():
                    results.append({"name": job_name, "status": "error",
                                    "message": f"Input not found: {input_path}"})
                    continue

                image_file = open(str(img_path), "rb")
                kwargs = {
                    "model": model, "image": image_file, "prompt": prompt, "n": 1,
                }
                if size != "auto":
                    kwargs["size"] = size
                if quality != "auto":
                    kwargs["quality"] = quality
                if model.startswith("gpt-image"):
                    kwargs["output_format"] = fmt
                    if compression is not None:
                        kwargs["output_compression"] = compression
                    if background != "auto":
                        kwargs["background"] = background
                    if input_fidelity:
                        kwargs["input_fidelity"] = input_fidelity

                try:
                    result = api_call_with_retry(lambda: client.images.edit(**kwargs), retries, seekables=[image_file])
                finally:
                    image_file.close()
            else:
                # Generate mode
                kwargs = {"model": model, "prompt": prompt, "n": 1}
                if size != "auto":
                    kwargs["size"] = size
                if quality != "auto":
                    kwargs["quality"] = quality
                if model.startswith("gpt-image"):
                    kwargs["output_format"] = fmt
                    if compression is not None:
                        kwargs["output_compression"] = compression
                    if background != "auto":
                        kwargs["background"] = background

                result = api_call_with_retry(lambda: client.images.generate(**kwargs), retries)

            b64 = result.data[0].b64_json
            if b64:
                save_image(b64, out_path, fmt)
                verify_output(out_path)
                tag_image(out_path, fmt, prompt, model, quality, size)
                results.append({"name": job_name, "status": "success", "path": str(out_path)})
            else:
                url = result.data[0].url
                results.append({"name": job_name, "status": "success", "url": url})

        except ImageCLIError as e:
            results.append({"name": job_name, "status": "error",
                            "type": e.typ, "message": str(e)})
            continue

    succeeded = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - succeeded

    # Generate HTML gallery
    gallery_path = generate_gallery_html(output_dir, results, manifest)

    # Don't use success() here because we want to include failures too
    print(json.dumps({
        "status": "success" if failed == 0 else "partial",
        "message": f"Batch complete: {succeeded}/{len(results)} succeeded",
        "gallery": gallery_path,
        "results": results,
    }, indent=2))
    sys.exit(0 if failed == 0 else 1)


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OpenAI Images API wrapper for generation, editing, and analysis."
    )
    parser.add_argument(
        "--retries", type=int, default=0,
        help="Retry transient API errors N times with exponential backoff. Default: 0",
    )
    parser.add_argument(
        "--prefix",
        help="Style prefix prepended to prompts (generate, edit, style-transfer)",
    )
    parser.add_argument(
        "--preset", choices=["draft", "balanced", "final"],
        help="Quality preset: draft (mini/low), balanced (1.5/medium), final (1.5/high)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Estimate cost without making API calls",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # -- Shared arguments --------------------------------------------------
    def add_common_args(p):
        p.add_argument(
            "--model", default="gpt-image-1.5",
            help="Model to use (gpt-image-1.5, gpt-image-1, gpt-image-1-mini, dall-e-3). Default: gpt-image-1.5",
        )
        p.add_argument(
            "--size", default="auto",
            choices=["auto", "1024x1024", "1536x1024", "1024x1536", "1792x1024", "1024x1792"],
            help="Output image size. Default: auto",
        )
        p.add_argument(
            "--quality", default="auto",
            choices=["auto", "low", "medium", "high", "standard", "hd"],
            help="Image quality. Default: auto",
        )
        p.add_argument(
            "--format", default="png",
            choices=["png", "jpeg", "webp"],
            help="Output format. Default: png",
        )
        p.add_argument(
            "--compression", type=int, default=None,
            help="Output compression 0-100 (jpeg/webp only)",
        )
        p.add_argument(
            "--background", default="auto",
            choices=["auto", "transparent", "opaque"],
            help="Background transparency. Default: auto",
        )
        p.add_argument(
            "-n", type=int, default=1,
            help="Number of images to generate. Default: 1",
        )
        p.add_argument(
            "--output", "-o",
            help="Explicit output file path (single image only)",
        )
        p.add_argument(
            "--output-dir", default=".",
            help="Directory for output files. Default: current directory",
        )

    # -- generate ----------------------------------------------------------
    gen_parser = subparsers.add_parser("generate", help="Generate image(s) from a text prompt")
    gen_parser.add_argument("prompt", help="Text description of the image to generate")
    add_common_args(gen_parser)

    # -- edit --------------------------------------------------------------
    edit_parser = subparsers.add_parser("edit", help="Edit existing image(s) with a text prompt")
    edit_parser.add_argument("prompt", help="Text description of the desired edit")
    edit_parser.add_argument(
        "--image", "-i", required=True, nargs="+",
        help="Path(s) to input image(s). Up to 16 for GPT image models.",
    )
    edit_parser.add_argument(
        "--mask", "-m",
        help="Path to mask PNG (transparent areas = edit regions)",
    )
    edit_parser.add_argument(
        "--input-fidelity", choices=["low", "high"], default=None,
        help="How closely to match input image structure. high=preserve layout, low=loose reference (API default: low)",
    )
    add_common_args(edit_parser)

    # -- describe ----------------------------------------------------------
    desc_parser = subparsers.add_parser(
        "describe", help="Analyze image(s) with GPT-4o vision",
    )
    desc_parser.add_argument("image", nargs="+", help="Path(s) to image file(s) to describe")
    desc_parser.add_argument(
        "--mode", default="alt-text",
        choices=["alt-text", "caption", "detailed", "tags", "json"],
        help="Output mode. Default: alt-text",
    )
    desc_parser.add_argument(
        "--custom",
        help="Freeform analysis prompt (overrides --mode)",
    )
    desc_parser.add_argument(
        "--model", default="gpt-4o-mini",
        choices=["gpt-4o", "gpt-4o-mini"],
        help="Vision model. Default: gpt-4o-mini (cheaper)",
    )

    # -- bg-remove ---------------------------------------------------------
    bg_parser = subparsers.add_parser(
        "bg-remove", help="Remove background from an image (transparent PNG)",
    )
    bg_parser.add_argument("image", help="Path to the input image")
    bg_parser.add_argument("--output", "-o", help="Explicit output file path")
    bg_parser.add_argument("--output-dir", default=".", help="Directory for output files")
    bg_parser.add_argument("--model", default="gpt-image-1.5", help="Model. Default: gpt-image-1.5")
    bg_parser.add_argument(
        "--quality", default="auto",
        choices=["auto", "low", "medium", "high", "standard", "hd"],
        help="Image quality. Default: auto",
    )

    # -- style-transfer ----------------------------------------------------
    style_parser = subparsers.add_parser(
        "style-transfer", help="Apply an artistic style to an image",
    )
    style_parser.add_argument("image", help="Path to the input image")
    style_parser.add_argument(
        "--style", required=True, choices=STYLE_CHOICES,
        help="Style preset, or 'custom' with --custom-style",
    )
    style_parser.add_argument("--custom-style", help="Freeform style description (required when --style custom)")
    style_parser.add_argument("--output", "-o", help="Explicit output file path")
    style_parser.add_argument("--output-dir", default=".", help="Directory for output files")
    style_parser.add_argument("--model", default="gpt-image-1.5", help="Model. Default: gpt-image-1.5")
    style_parser.add_argument(
        "--size", default="auto",
        choices=["auto", "1024x1024", "1536x1024", "1024x1536", "1792x1024", "1024x1792"],
        help="Output size. Default: auto",
    )
    style_parser.add_argument(
        "--quality", default="auto",
        choices=["auto", "low", "medium", "high", "standard", "hd"],
        help="Image quality. Default: auto",
    )
    style_parser.add_argument(
        "--format", default="png", choices=["png", "jpeg", "webp"],
        help="Output format. Default: png",
    )

    # -- restore -----------------------------------------------------------
    restore_parser = subparsers.add_parser(
        "restore", help="Restore a damaged, faded, or degraded photograph",
    )
    restore_parser.add_argument("image", help="Path to the input image")
    restore_parser.add_argument("--output", "-o", help="Explicit output file path")
    restore_parser.add_argument("--output-dir", default=".", help="Directory for output files")
    restore_parser.add_argument("--model", default="gpt-image-1.5", help="Model. Default: gpt-image-1.5")
    restore_parser.add_argument(
        "--size", default="auto",
        choices=["auto", "1024x1024", "1536x1024", "1024x1536", "1792x1024", "1024x1792"],
        help="Output size. Default: auto",
    )
    restore_parser.add_argument(
        "--quality", default="auto",
        choices=["auto", "low", "medium", "high", "standard", "hd"],
        help="Image quality. Default: auto",
    )
    restore_parser.add_argument(
        "--format", default="png", choices=["png", "jpeg", "webp"],
        help="Output format. Default: png",
    )

    # -- thumbnail ---------------------------------------------------------
    thumb_parser = subparsers.add_parser(
        "thumbnail", help="Generate or adapt an image as a web-ready thumbnail",
    )
    thumb_parser.add_argument("prompt", nargs="?", default=None, help="Text prompt (or guidance with --from-image)")
    thumb_parser.add_argument("--from-image", help="Path to existing image to adapt as thumbnail")
    thumb_parser.add_argument("--output", "-o", help="Explicit output file path")
    thumb_parser.add_argument("--output-dir", default=".", help="Directory for output files")
    thumb_parser.add_argument("--model", default="gpt-image-1.5", help="Model. Default: gpt-image-1.5")
    thumb_parser.add_argument(
        "--format", default="jpeg", choices=["png", "jpeg", "webp"],
        help="Output format. Default: jpeg",
    )
    thumb_parser.add_argument("--compression", type=int, default=80, help="Compression 0-100. Default: 80")
    thumb_parser.add_argument(
        "--quality", default="auto",
        choices=["auto", "low", "medium", "high", "standard", "hd"],
        help="Image quality. Default: auto",
    )

    # -- batch -------------------------------------------------------------
    batch_parser = subparsers.add_parser(
        "batch", help="Process multiple image jobs from a JSON manifest",
    )
    batch_parser.add_argument("manifest", help="Path to JSON manifest file")
    batch_parser.add_argument("--output-dir", default=".", help="Base directory for output files")

    args = parser.parse_args()
    apply_preset(args)

    try:
        if args.command == "generate":
            command_generate(args)
        elif args.command == "edit":
            command_edit(args)
        elif args.command == "describe":
            command_describe(args)
        elif args.command == "bg-remove":
            command_bg_remove(args)
        elif args.command == "style-transfer":
            command_style_transfer(args)
        elif args.command == "restore":
            command_restore(args)
        elif args.command == "thumbnail":
            command_thumbnail(args)
        elif args.command == "batch":
            command_batch(args)
    except ImageCLIError as e:
        error(str(e), e.typ, e.fix)
    except SystemExit:
        raise
    except Exception as exc:
        err_msg = str(exc) or repr(exc)
        tb_str = traceback.format_exc()

        log_dir = Path.home() / ".openai_image" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "error.log"
        with open(log_file, "a") as f:
            f.write(
                f"--- UNHANDLED EXCEPTION [openai_image.py] ---\n"
                f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
                f"Command: {' '.join(sys.argv)}\n"
                f"{tb_str}\n"
            )

        print(json.dumps({
            "status": "error",
            "type": "UnhandledException",
            "message": err_msg,
            "fix": (
                "AGENT DIRECTIVE: This is an internal bug in openai_image.py. "
                "Document this failure in the skill's KNOWN_BUGS.md and notify the user."
            ),
            "logFile": str(log_file),
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
