import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

os.environ["TESSDATA_PREFIX"] = r"C:/Program Files/Tesseract-OCR/tessdata/"
POPPLER_PATH = r"C:/Program Files/poppler-24.08.0/Library/bin"

def extract_text(file_path,lang='eng+sin+tam'):
    text = ""

    if file_path.lower().endswith(".pdf"):
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        for page_num, image in enumerate(images):
            page_text = pytesseract.image_to_string(image,lang=lang)
            text += f"\n\n--- Page {page_num + 1} ---\n{page_text}"
    else:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image,lang=lang)

    print(text)
    return text
