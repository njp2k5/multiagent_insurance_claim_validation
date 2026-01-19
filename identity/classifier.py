import cv2
from identity.image_utils import resize_max
from identity.ocr_utils import (
    ocr_image,
    extract_aadhaar_numbers,
    is_aadhaar_doc,
    extract_name_from_aadhaar,
    extract_age_from_aadhaar
)
from identity.aadhar_validator import verhoeff_validate

class AadhaarClassifier:
    def classify(self, image_path: str):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError("Invalid image path")

        image = resize_max(image)
        text = ocr_image(image)

        numbers = extract_aadhaar_numbers(text)
        verified = {n: verhoeff_validate(n) for n in numbers}
        name = extract_name_from_aadhaar(text)
        age = extract_age_from_aadhaar(text)

        return {
            "aadhaar_numbers": numbers,
            "verified": verified,
            "is_aadhaar": is_aadhaar_doc(text),
            "aadhaar_name": name,
            "aadhaar_age": age
        }
