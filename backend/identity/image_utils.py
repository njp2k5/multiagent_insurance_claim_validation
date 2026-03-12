import numpy as np

_cv2 = None

def _get_cv2():
    """Lazy load cv2 to speed up startup."""
    global _cv2
    if _cv2 is None:
        import cv2
        _cv2 = cv2
    return _cv2


def resize_max(image, max_dim=1200):
    h, w = image.shape[:2]
    if max(h, w) <= max_dim:
        return image
    scale = max_dim / float(max(h, w))
    cv2 = _get_cv2()
    return cv2.resize(image, (int(w*scale), int(h*scale)))
