# PDF Unlocker (Python)

A tiny Python app to take a password-protected PDF and save an unlocked copy (no password). Works as a command-line tool or a simple GUI.

## Features
- Decrypts user-password protected PDFs (owner-permissions will also be cleared in the output).
- CLI and optional Tkinter GUI (`--gui`).
- Preserves pages and (best-effort) metadata.
- Creates an output file named `<original>_unlocked.pdf` by default.

## Install
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage (CLI)
```bash
python unlock_pdf.py path/to/locked.pdf -o path/to/unlocked.pdf -p "yourpassword"
```
If you omit `-o`, the output defaults to `locked_unlocked.pdf` in the same folder.
If you omit `-p`, you will be prompted securely in the terminal.

## Usage (GUI)
```bash
python unlock_pdf.py --gui
```
- Pick the locked PDF
- Enter the password (or leave blank to try an empty password)
- Choose where to save the unlocked PDF

## Notes
- This uses `pypdf` (pure-Python). For very old/rare encryption schemes, use `pikepdf` (QPDF backend) instead.
- Only decrypt PDFs you own or have permission to process.
- If you see "Incorrect password or unsupported encryption", verify the password and try with the latest `pypdf` version.

## Troubleshooting
- **tkinter not found**: Some minimal Python builds omit Tk. Use CLI mode or install a Python that includes Tk.
- **Still encrypted after saving**: Ensure you are opening the *new* `_unlocked.pdf` file; the app never writes over the original unless you choose the same path.
