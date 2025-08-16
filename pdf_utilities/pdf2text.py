import os
import PyPDF2

def convert_pdf_to_txt(pdf_path, output_txt_path=None):
    if not os.path.isfile(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            text += f"\n\n--- Page {i + 1} ---\n"
            text += page_text if page_text else "[No extractable text]"

    if not output_txt_path:
        output_txt_path = os.path.splitext(pdf_path)[0] + ".txt"

    with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)

    print(f"✅ Text extracted and saved to: {output_txt_path}")

if __name__ == "__main__":
    pdf_file = input("Enter path to the PDF file: ").strip()
    convert_pdf_to_txt(pdf_file)


