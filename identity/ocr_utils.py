import re
import pytesseract
from PIL import Image
import cv2

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

AADHAAR_REGEX = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
AADHAAR_KEYWORDS = ['aadhaar', 'aadhar', 'uidai', 'government of india']

def extract_aadhaar_numbers(text: str):
    return [re.sub(r'\D', '', m) for m in AADHAAR_REGEX.findall(text)]

def is_aadhaar_doc(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in AADHAAR_KEYWORDS)

def ocr_image(image):
    pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    return pytesseract.image_to_string(pil, config="--psm 6")
