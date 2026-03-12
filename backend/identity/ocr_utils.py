import re
from datetime import datetime
from PIL import Image

_cv2 = None
_pytesseract = None


def _get_cv2():
    """Lazy load cv2."""
    global _cv2
    if _cv2 is None:
        import cv2
        _cv2 = cv2
    return _cv2


def _get_pytesseract():
    """Lazy load pytesseract."""
    global _pytesseract
    if _pytesseract is None:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
        _pytesseract = pytesseract
    return _pytesseract


AADHAAR_REGEX = re.compile(r'\b\d{4}\s?\d{4}\s?\d{4}\b')
AADHAAR_KEYWORDS = ['aadhaar', 'aadhar', 'uidai', 'government of india']
NAME_REGEX = re.compile(r'name[:\-]?\s*([A-Z][A-Z\s\.]+)', re.IGNORECASE)
DOB_REGEX = re.compile(r'(\d{2})[/\-](\d{2})[/\-](\d{4})')
AGE_REGEX = re.compile(r'age[:\-]?\s*(\d{1,3})', re.IGNORECASE)

def extract_aadhaar_numbers(text: str):
    return [re.sub(r'\D', '', m) for m in AADHAAR_REGEX.findall(text)]

def is_aadhaar_doc(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in AADHAAR_KEYWORDS)

def extract_name_from_aadhaar(text: str):
    """Extract name from Aadhaar card OCR text."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    def _clean_name(raw: str):
        # Remove common relationship prefixes and non-alpha noise
        cleaned = re.sub(r'\b(S/O|D/O|W/O|C/O)\b[:\-]?', '', raw, flags=re.IGNORECASE)
        cleaned = re.sub(r'[^A-Za-z\s\.]', ' ', cleaned)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned).strip(' .')
        if cleaned and 2 < len(cleaned) <= 60:
            words = cleaned.split()
            if 1 <= len(words) <= 5:
                return cleaned
        return None

    # Strategy 0: If a DOB line exists, take the line immediately above it as name
    for i, line in enumerate(lines):
        if DOB_REGEX.search(line):
            if i > 0:
                # Walk upwards a couple of lines to skip blank/noisy headers
                for j in range(i - 1, max(-1, i - 4), -1):
                    candidate = lines[j].strip()
                    cleaned = _clean_name(candidate)
                    if cleaned:
                        return cleaned
            break
    
    # Strategy 1: Find line after "Name:" or similar pattern
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(pattern in line_lower for pattern in ['name:', 'name', 'नाम']):
            # Name might be on same line after colon/space
            parts = re.split(r'[:\-]\s*', line, maxsplit=1)
            if len(parts) > 1 and parts[1].strip():
                name_candidate = parts[1].strip()
                if re.match(r'^[A-Za-z\s\.]+$', name_candidate) and len(name_candidate) > 2:
                    return name_candidate
            # Name might be on next line
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if re.match(r'^[A-Za-z\s\.]+$', next_line) and len(next_line) > 2:
                    return next_line
    
    # Strategy 2: Find prominent text line that looks like a name
    # Skip lines with keywords, numbers, or special patterns
    excluded_patterns = ['government', 'india', 'uidai', 'aadhaar', 'aadhar', 'dob', 'year', 
                         'birth', 'male', 'female', r'\d{4}', r'\d{2}/\d{2}/\d{4}']
    
    for line in lines[:10]:  # Check first 10 lines only
        line_lower = line.lower()
        # Skip if contains excluded keywords or patterns
        if any(excl in line_lower for excl in excluded_patterns if not excl.startswith(r'\d')):
            continue
        if any(re.search(excl, line) for excl in excluded_patterns if excl.startswith(r'\d')):
            continue
        # Check if it's mostly alphabetic with reasonable length
        if re.match(r'^[A-Z][A-Za-z\s\.]{2,50}$', line):
            word_count = len(line.split())
            if 1 <= word_count <= 5:  # Typical name has 1-5 words
                return line
    
    return None


def extract_age_from_aadhaar(text: str):
    """Extract age from Aadhaar card OCR text."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    
    # Try to find explicit age field
    for line in lines:
        match = AGE_REGEX.search(line)
        if match:
            age_val = int(match.group(1))
            if 0 < age_val < 130:
                return age_val
    
    # Try to calculate from DOB
    for line in lines:
        match = DOB_REGEX.search(line)
        if match:
            day, month, year = match.groups()
            year_val = int(year)
            current_year = datetime.now().year
            if 1900 < year_val <= current_year:
                age_val = current_year - year_val
                if 0 < age_val < 130:
                    return age_val
    
    return None


def ocr_image(image):
    cv2 = _get_cv2()
    pytesseract = _get_pytesseract()
    pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    return pytesseract.image_to_string(pil, config="--psm 6")
