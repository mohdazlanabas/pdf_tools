#!/usr/bin/env python3
"""
PDF Compressor (CLI-only, pikepdf/QPDF backend)

Usage:
    python compress.py input.pdf output.pdf [-p PASSWORD] [--no-linearize]

Examples:
    python compress.py report.pdf report_compressed.pdf
    python compress.py secret.pdf smaller.pdf -p "mypassword"

Notes:
- Focuses on structural compression (object streams, deflated streams, linearization).
- Does NOT downscale images. For stronger size reduction, use an image-downscaling workflow.
"""
import sys
from pathlib import Path
import argparse
import pikepdf


def compress_pdf(input_path: Path, output_path: Path, password: str | None = None, linearize: bool = True):
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # pikepdf.open expects a string path or a stream and password must be a string.
    pw = "" if (password is None) else password

    # Open by path (lets pikepdf manage the file handle)
    with pikepdf.open(str(input_path), password=pw) as pdf:
        pdf.save(
            str(output_path),
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            linearize=linearize,
        )

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Compress a PDF (recompress streams, object streams, linearize).")
    parser.add_argument("input", help="Path to the input PDF")
    parser.add_argument("output", help="Path to the output (compressed) PDF")
    parser.add_argument("-p", "--password", help="Password if the input PDF is encrypted")
    parser.add_argument("--no-linearize", action="store_true", help="Disable linearization (Fast Web View)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        out = compress_pdf(
            input_path=input_path,
            output_path=output_path,
            password=args.password,
            linearize=not args.no_linearize,
        )
        print(f"✅ Compressed PDF saved to: {out}")
    except pikepdf._qpdf.PasswordError:
        print("❌ Error: Incorrect password (or password required). Try: -p \"yourpassword\"")
        sys.exit(2)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
