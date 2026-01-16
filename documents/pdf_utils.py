from pdf2image import convert_from_path
import os
import uuid

def pdf_to_images(pdf_path: str, output_dir: str) -> list[str]:
    images = convert_from_path(pdf_path, dpi=300)
    image_paths = []

    for img in images:
        path = os.path.join(output_dir, f"{uuid.uuid4()}.png")
        img.save(path, "PNG")
        image_paths.append(path)

    return image_paths
