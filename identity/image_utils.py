import cv2
import numpy as np

def resize_max(image, max_dim=1200):
    h, w = image.shape[:2]
    if max(h, w) <= max_dim:
        return image
    scale = max_dim / float(max(h, w))
    return cv2.resize(image, (int(w*scale), int(h*scale)))
