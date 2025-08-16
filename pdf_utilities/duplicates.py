import os
import shutil

# Folder to scan and folder to move PDFs
scan_folder = os.path.expanduser("~/Documents")
move_folder = os.path.expanduser("~/Downloads/ddeletee")
os.makedirs(move_folder, exist_ok=True)

# File types to look for
extensions = ['.doc', '.docx', '.odt', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf']

# Collect filenames without extensions
names = {}
for root, _, files in os.walk(scan_folder):
    for f in files:
        name, ext = os.path.splitext(f)
        if ext.lower() in extensions:
            full_path = os.path.join(root, f)
            if name in names:
                names[name].append((ext.lower(), full_path))
            else:
                names[name] = [(ext.lower(), full_path)]

# Find duplicates
duplicates = {k: v for k, v in names.items() if len(v) > 1}

# Process duplicates
for name, files in duplicates.items():
    print(f"\nDuplicate group: {name}")
    for ext, path in files:
        print(f"  {ext} - {path}")

    pdf_files = [path for ext, path in files if ext == ".pdf"]
    non_pdf_files = [path for ext, path in files if ext != ".pdf"]

    if pdf_files:
        if not non_pdf_files:
            # Only PDFs in group: Keep latest, delete others
            pdf_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            keep_pdf = pdf_files[0]
            delete_pdfs = pdf_files[1:]

            print(f"Keeping latest PDF: {keep_pdf}")
            for pdf_path in delete_pdfs:
                try:
                    os.remove(pdf_path)
                    print(f"Deleted older PDF: {pdf_path}")
                except Exception as e:
                    print(f"Error deleting {pdf_path}: {e}")
        else:
            # PDFs + other file types: Move PDFs to ddeletee
            print(f"Moving PDF file(s) from this group to: {move_folder}")
            for pdf_path in pdf_files:
                try:
                    shutil.move(pdf_path, move_folder)
                    print(f"Moved: {pdf_path}")
                except Exception as e:
                    print(f"Error moving {pdf_path}: {e}")

print(f"\n✅ Done. Check '{move_folder}' in Downloads for moved PDFs.")
