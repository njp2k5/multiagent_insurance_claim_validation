import re
import hashlib
from PIL import Image
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

_cv2 = None
_pytesseract = None

# OCR result cache
_ocr_cache: dict[str, str] = {}


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


def _get_file_hash(path: str) -> str:
    """Get hash of file for caching."""
    try:
        with open(path, 'rb') as f:
            # Read first 8KB for fast hashing
            return hashlib.md5(f.read(8192)).hexdigest()
    except:
        return path


def extract_text_from_image(path: str, use_cache: bool = True) -> str:
    """
    Extract text from image with caching.
    
    Optimizations:
    - Cache OCR results by file hash
    - Reduced image scaling (1.5x instead of 2x)
    - Optimized Tesseract config
    """
    file_hash = None
    
    # Check cache
    if use_cache:
        file_hash = _get_file_hash(path)
        if file_hash in _ocr_cache:
            return _ocr_cache[file_hash]
    
    cv2 = _get_cv2()
    pytesseract = _get_pytesseract()
    
    image = cv2.imread(path)
    if image is None:
        return ""

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Reduced scaling for faster processing
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

    pil = Image.fromarray(gray)
    # Optimized Tesseract config for speed
    text = pytesseract.image_to_string(pil, config="--psm 6 --oem 1")
    
    # Cache result
    if use_cache and file_hash:
        _ocr_cache[file_hash] = text
        # Limit cache size
        if len(_ocr_cache) > 100:
            keys = list(_ocr_cache.keys())[:50]
            for k in keys:
                del _ocr_cache[k]
    
    return text


def extract_text_from_images_parallel(paths: List[str], max_workers: int = 2) -> List[str]:
    """
    Extract text from multiple images in parallel.
    
    Args:
        paths: List of image paths
        max_workers: Maximum parallel OCR threads (default 2 to avoid CPU overload)
    
    Returns:
        List of extracted texts in same order as input paths
    """
    if not paths:
        return []
    
    if len(paths) == 1:
        return [extract_text_from_image(paths[0])]
    
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(extract_text_from_image, path): (i, path) 
            for i, path in enumerate(paths)
        }
        for future in as_completed(future_to_path):
            idx, path = future_to_path[future]
            try:
                results[idx] = future.result()
            except Exception:
                results[idx] = ""
    
    return [results.get(i, "") for i in range(len(paths))]


def clear_ocr_cache():
    """Clear the OCR cache."""
    _ocr_cache.clear()


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
