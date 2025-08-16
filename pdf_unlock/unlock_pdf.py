#!/usr/bin/env python3
"""
PDF Unlocker
- Upload/choose a password-protected (encrypted) PDF
- Enter the password
- Save an unlocked copy (no password)

Usage (CLI):
  python unlock_pdf.py input.pdf -o output.pdf -p "yourpassword"

GUI mode:
  python unlock_pdf.py --gui

Dependencies:
  pip install pypdf
"""
import sys
import argparse
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, simpledialog, messagebox
except Exception:
    # tkinter may not be available in some environments; CLI will still work
    tk = None

from pypdf import PdfReader, PdfWriter


def unlock_pdf(input_path: Path, output_path: Path, password: str | None) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    with open(input_path, "rb") as f:
        reader = PdfReader(f, strict=False)

        if reader.is_encrypted:
            # Try empty password first (some PDFs use blank password)
            ok = False
            try:
                res = reader.decrypt("" if password is None else password)
                # pypdf returns an int/boolean depending on version
                ok = bool(res)
            except Exception as e:
                raise RuntimeError(f"Failed to decrypt PDF: {e}") from e

            if not ok:
                raise PermissionError("Incorrect password or unsupported encryption.")

        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Copy metadata if present
        try:
            if getattr(reader, "metadata", None):
                writer.add_metadata({k: v for k, v in reader.metadata.items() if v is not None})
        except Exception:
            pass  # metadata copy is best-effort

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write unlocked (no encryption) PDF
        with open(output_path, "wb") as out_f:
            writer.write(out_f)


def run_cli():
    parser = argparse.ArgumentParser(description="Unlock a password-protected PDF.")
    parser.add_argument("input", nargs="?", help="Path to the input (locked) PDF")
    parser.add_argument("-o", "--output", help="Path to save the unlocked PDF")
    parser.add_argument("-p", "--password", help="Password to unlock the PDF (omit to be prompted securely)")
    parser.add_argument("--gui", action="store_true", help="Launch a simple GUI instead of CLI")

    args = parser.parse_args()

    if args.gui:
        if tk is None:
            print("Tkinter not available. Please use CLI mode.", file=sys.stderr)
            sys.exit(2)
        return run_gui()

    if not args.input:
        parser.print_help()
        sys.exit(1)

    input_path = Path(args.input)

    if args.password is None:
        # Prompt securely in terminal
        try:
            import getpass
            password = getpass.getpass("Enter PDF password (leave empty if you want to try blank): ")
        except Exception:
            password = input("Enter PDF password (input not hidden): ")
    else:
        password = args.password

    output_path = Path(args.output) if args.output else input_path.with_stem(input_path.stem + "_unlocked")

    try:
        unlock_pdf(input_path, output_path, password if password != "" else None)
        print(f"✅ Unlocked PDF saved to: {output_path}")
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(4)


def run_gui():
    root = tk.Tk()
    root.withdraw()
    root.update()

    in_path = filedialog.askopenfilename(
        title="Select locked PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not in_path:
        return

    pwd = simpledialog.askstring("PDF Password", "Enter password (leave empty to try blank):", show="*")
    # choose output
    default_out = str(Path(in_path).with_stem(Path(in_path).stem + "_unlocked"))
    out_path = filedialog.asksaveasfilename(
        title="Save unlocked PDF as",
        defaultextension=".pdf",
        initialfile=Path(default_out).name,
        filetypes=[("PDF files", "*.pdf")]
    )
    if not out_path:
        return

    try:
        unlock_pdf(Path(in_path), Path(out_path), None if (pwd is None or pwd == "") else pwd)
        messagebox.showinfo("Success", f"Unlocked PDF saved to:\n{out_path}")
    except FileNotFoundError as e:
        messagebox.showerror("File Not Found", str(e))
    except PermissionError as e:
        messagebox.showerror("Decryption Failed", str(e))
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error:\n{e}")


if __name__ == "__main__":
    run_cli()

