#!/usr/bin/env python3
import argparse
import json
import sys
import subprocess
import os
import shutil
from pathlib import Path

def success(data=None):
    if data is None: data = {}
    print(json.dumps({"status": "success", **data}, indent=2))
    sys.exit(0)

def error(message, typ="Error", fix=None):
    ret = {"status": "error", "message": message, "type": typ}
    if fix: ret["fix"] = fix
    print(json.dumps(ret, indent=2))
    sys.exit(1)

def ensure_command(cmd):
    if not shutil.which(cmd):
        error(f"Required command '{cmd}' is not installed.", fix=f"Run bash scripts/setup.sh to install {cmd}")

def command_pdf(args):
    """
    Produce a searchable PDF from a scanned PDF or an image.
    Uses ocrmypdf under the hood.
    """
    ensure_command("ocrmypdf")
    
    input_file = Path(args.input).resolve()
    if not input_file.exists():
        error(f"Input file not found: {args.input}", "FileNotFound")
    
    output_file = Path(args.output).resolve() if args.output else input_file
    
    cmd = ["ocrmypdf"]
    
    # Core flags for fixing scanned files based on user requests (autorotate, deskew)
    if not args.no_rotate:
        cmd.append("--rotate-pages")
    if not args.no_deskew:
        cmd.append("--deskew")
    
    # Crucial flag to avoid reprocessing PDFs that already have text
    if not args.force:
        cmd.append("--skip-text")
    
    # If the input is not a PDF (e.g. an image), specify image mode
    ext = input_file.suffix.lower()
    if ext != ".pdf":
        cmd.append("--image-dpi")
        cmd.append("300")
        
    cmd.extend([str(input_file), str(output_file)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except Exception as e:
        error(f"Execution failed: {e}")
        
    if result.returncode == 0:
        success({"message": "OCR completed successfully", "output": str(output_file), "stderr": result.stderr})
    elif result.returncode == 6:
        # Exit code 6 in ocrmypdf indicates the file already contained text and was skipped
        success({"message": "File already contains text, skipped processing (--skip-text)", "output": str(output_file)})
    else:
        error(f"ocrmypdf failed with exit code {result.returncode}", "OcrError", fix=result.stderr)

def command_text(args):
    """
    Extract raw text from a PDF or image without creating a searchable PDF.
    Useful for agents that need to read the content natively.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        error("Python dependencies missing.", fix="uv pip install -r requirements.txt")
        
    ensure_command("tesseract")
    
    input_file = Path(args.input).resolve()
    if not input_file.exists():
        error(f"Input file not found: {args.input}", "FileNotFound")
    
    ext = input_file.suffix.lower()
    text = ""
    
    if ext == ".pdf":
        ensure_command("pdftotext")
        # Fast path: check if PDF already has embedded text
        cmd = ["pdftotext", str(input_file), "-"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            text = result.stdout.strip()
        else:
            # Fallback path: rasterize the PDF to images and OCR them
            try:
                from pdf2image import convert_from_path
            except ImportError:
                error("pdf2image missing.", fix="uv pip install pdf2image")
            ensure_command("pdftoppm")
            
            pages = convert_from_path(str(input_file), dpi=300)
            page_texts = []
            for page in pages:
                page_texts.append(pytesseract.image_to_string(page))
            text = "\n\n".join(page_texts)
    else:
        # Standard image OCR
        img = Image.open(str(input_file))
        text = pytesseract.image_to_string(img)
        
    success({"text": text})

def command_batch(args):
    """
    Process an entire directory of PDFs and images in-place.
    Skips files that already contain text.
    """
    ensure_command("ocrmypdf")
    
    input_dir = Path(args.directory).resolve()
    if not input_dir.is_dir():
        error(f"Directory not found: {args.directory}", "FileNotFound")
        
    results = {"processed": [], "skipped": [], "errors": []}
    
    for ext in [".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff"]:
        for file in input_dir.rglob(f"*{ext}"):
            if file.suffix.lower() != ext: continue
            
            cmd = ["ocrmypdf", "--rotate-pages", "--deskew"]
            if not args.force:
                cmd.append("--skip-text")
                
            if ext != ".pdf":
                cmd.extend(["--image-dpi", "300"])
                # ocrmypdf converts images to pdf; we need to change output extension
                out_file = file.with_suffix(".pdf")
            else:
                out_file = file
                
            cmd.extend([str(file), str(out_file)])
            
            # Run without stdout/stderr buffering block, capturing instead
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if res.returncode == 0:
                results["processed"].append(str(file))
                # Delete original image if we generated a new PDF and requested cleanup
                if ext != ".pdf" and args.clean_images:
                    file.unlink()
            elif res.returncode == 6:
                results["skipped"].append(str(file))
            else:
                results["errors"].append({"file": str(file), "error": res.stderr.strip()})
                
    success(results)

def main():
    parser = argparse.ArgumentParser(description="OCR Pipeline wrapper for GPU-accelerated environments.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # pdf command
    pdf_parser = subparsers.add_parser("pdf", help="Generate a searchable PDF from an image or scanned PDF")
    pdf_parser.add_argument("input", help="Path to input file")
    pdf_parser.add_argument("--output", "-o", help="Optional path to output file. Defaults to overwriting the input file inline.")
    pdf_parser.add_argument("--force", action="store_true", help="Force OCR even if the file already contains text")
    pdf_parser.add_argument("--no-rotate", action="store_true", help="Disable automatic page rotation detection")
    pdf_parser.add_argument("--no-deskew", action="store_true", help="Disable page deskew (straightening)")

    # text command
    text_parser = subparsers.add_parser("text", help="Extract raw text directly from an image or scanned PDF")
    text_parser.add_argument("input", help="Path to input file")
    
    # batch command
    batch_parser = subparsers.add_parser("batch", help="Process an entire directory of images and PDFs recursively")
    batch_parser.add_argument("directory", help="Path to directory containing files")
    batch_parser.add_argument("--force", action="store_true", help="Force OCR on PDFs even if they already contain text")
    batch_parser.add_argument("--clean-images", action="store_true", help="Delete original individual images after converting them to searchable PDFs")

    args = parser.parse_args()

    if args.command == "pdf":
        command_pdf(args)
    elif args.command == "text":
        command_text(args)
    elif args.command == "batch":
        command_batch(args)

if __name__ == "__main__":
    main()
