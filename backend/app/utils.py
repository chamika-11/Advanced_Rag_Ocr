from pdf2image import convert_from_path
import os

def convert_pdf_to_images(pdf_path, output_folder="data/pdf_pages", dpi=300):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path, dpi=dpi)
    image_paths = []

    for i, img in enumerate(images):
        image_path = os.path.join(output_folder, f"page_{i+1}.jpg")
        img.save(image_path, "JPEG")
        image_paths.append(image_path)

    return image_paths
