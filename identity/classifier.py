import cv2
from identity.image_utils import resize_max
from identity.ocr_utils import ocr_image, extract_aadhaar_numbers, is_aadhaar_doc
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

        return {
            "aadhaar_numbers": numbers,
            "verified": verified,
            "is_aadhaar": is_aadhaar_doc(text)
        }
