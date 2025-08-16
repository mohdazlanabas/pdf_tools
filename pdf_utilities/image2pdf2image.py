import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from PIL import Image
import fitz  # PyMuPDF

def convert_image_to_pdf(image_path, output_pdf_path=None):
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found at '{image_path}'")
        return

    if not output_pdf_path:
        base_name = os.path.splitext(image_path)[0]
        output_pdf_path = base_name + ".pdf"

    try:
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Determine page size based on image orientation
        if img_width > img_height:
            pagesize = landscape(A4)
        else:
            pagesize = A4

        c = canvas.Canvas(output_pdf_path, pagesize=pagesize)
        page_width, page_height = pagesize

        # Calculate scaling factor to fit image to page while maintaining aspect ratio
        width_ratio = page_width / img_width
        height_ratio = page_height / img_height
        scale_factor = min(width_ratio, height_ratio)

        scaled_width = img_width * scale_factor
        scaled_height = img_height * scale_factor

        # Center the image on the page
        x_offset = (page_width - scaled_width) / 2
        y_offset = (page_height - scaled_height) / 2

        c.drawImage(image_path, x_offset, y_offset, width=scaled_width, height=scaled_height)
        c.save()
        print(f"✅ Successfully converted '{image_path}' to '{output_pdf_path}'")

    except Exception as e:
        print(f"❌ An error occurred during image to PDF conversion: {e}")

def convert_pdf_to_image(pdf_path, output_folder=None, dpi=300):
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at '{pdf_path}'")
        return

    if not output_folder:
        output_folder = os.path.splitext(pdf_path)[0] + "_images"
    os.makedirs(output_folder, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            output_image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
            pix.save(output_image_path)
            print(f"✅ Saved page {page_num + 1} as '{output_image_path}'")
        doc.close()
        print(f"✅ Successfully converted '{pdf_path}' to images in '{output_folder}'")

    except Exception as e:
        print(f"❌ An error occurred during PDF to image conversion: {e}")

if __name__ == "__main__":
    print("🖼 File Converter: Image <-> PDF")
    while True:
        choice = input("\nChoose conversion type:\n1. Image to PDF\n2. PDF to Image\n(Enter 1 or 2): ").strip()

        if choice == '1':
            file_path = input("Enter image file path (e.g., image.jpg): ").strip()
            if file_path:
                convert_image_to_pdf(file_path)
            else:
                print("No image file path provided.")
            break
        elif choice == '2':
            file_path = input("Enter PDF file path (e.g., document.pdf): ").strip()
            if file_path:
                convert_pdf_to_image(file_path)
            else:
                print("No PDF file path provided.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")