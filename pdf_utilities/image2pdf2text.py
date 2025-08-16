import os
import pytesseract
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Optional: Windows path to Tesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def image_to_text(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def save_text_wrapped_pdf(text, pdf_path):
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()
    story = []

    for line in text.split('\n'):
        if line.strip():
            story.append(Paragraph(line.strip(), styles['Normal']))
            story.append(Spacer(1, 12))

    doc.build(story)

def convert_image_to_pdf(image_path, output_pdf_path=None):
    text = image_to_text(image_path)
    if not text.strip():
        print(f"No text found in {image_path}. Skipping.")
        return

    if not output_pdf_path:
        output_pdf_path = os.path.splitext(image_path)[0] + ".pdf"

    save_text_wrapped_pdf(text, output_pdf_path)
    print(f"✅ Saved OCR text from '{image_path}' to '{output_pdf_path}'")

if __name__ == "__main__":
    print("🖼 OCR Image to Searchable PDF (with text wrapping)")
    image_file = input("Enter image file path (e.g., image.jpg): ").strip()

    if not os.path.exists(image_file):
        print("❌ File not found.")
    else:
        convert_image_to_pdf(image_file)
