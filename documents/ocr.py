import pytesseract
import cv2
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def extract_text_from_image(path: str) -> str:
    image = cv2.imread(path)
    if image is None:
        return ""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    pil = Image.fromarray(gray)
    return pytesseract.image_to_string(pil, config="--psm 6")
