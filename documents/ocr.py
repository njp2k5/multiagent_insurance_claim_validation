import pytesseract
import cv2
import re
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


def extract_patient_name_and_age(text: str):
    """Extract name and age from medical/insurance documents."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    
    name = None
    age = None
    
    # Look for name patterns
    name_patterns = [
        r'(?:patient\s*)?name[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})',
        r'(?:full\s*)?name[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})',
        r'customer\s*name[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})',
        r'insured\s*name[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})',
    ]
    
    # Look for age patterns
    age_patterns = [
        r'age[:\-]?\s*(\d{1,3})\s*(?:years?|yrs?)?',
        r'age\s*[:/\-]\s*(\d{1,3})',
        r'(\d{1,3})\s*(?:years?|yrs?)',
    ]
    
    # Extract name - check first 20 lines
    for line in lines[:20]:
        if name:
            break
        line_lower = line.lower()
        for pattern in name_patterns:
            match = re.search(pattern, line_lower, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Clean up the name
                candidate = re.sub(r'[^A-Za-z\s\.]', ' ', candidate)
                candidate = re.sub(r'\s{2,}', ' ', candidate).strip()
                words = candidate.split()
                if 1 <= len(words) <= 5 and len(candidate) > 2:
                    name = candidate.title()
                    break
    
    # Extract age - check first 30 lines
    for line in lines[:30]:
        if age:
            break
        line_lower = line.lower()
        for pattern in age_patterns:
            match = re.search(pattern, line_lower, re.IGNORECASE)
            if match:
                age_val = int(match.group(1))
                if 0 < age_val < 130:
                    age = age_val
                    break
    
    return name, age
