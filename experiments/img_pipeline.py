import numpy as np
from scipy.ndimage import gaussian_filter # type: ignore
from PIL import Image, ImageFilter
from typing import Generator
from dataclasses import dataclass


# Physics constants
G = -1e-6  # Gravity constant (negative because lower = "downhill")

def convert_to_greyscale(img: Image.Image) -> Image.Image:
    return img.convert('L')

def convert_to_numpy(img: Image.Image) -> np.ndarray:
    return np.array(img, dtype=np.float64) / 255.0 # normalize between 0 and 1

def center_crop_square(img: np.ndarray) -> np.ndarray:
    h, w = img.shape
    size = min(h, w)  # target square size
    top = (h - size) // 2
    left = (w - size) // 2
    return img[top:top+size, left:left+size]

def invert_and_flatten_suface(img: np.ndarray) -> np.ndarray:
    img = 1 - img
    img /= 400 # we flatten the height map
    return img

def blur_the_image(img: np.ndarray) -> np.ndarray:
    SIGMA = 1.8
    return gaussian_filter(img, sigma=SIGMA) # type: ignore

def process_image(img: Image.Image) -> np.ndarray:
    img = convert_to_greyscale(img)
    img_surface = convert_to_numpy(img)
    img_surface = center_crop_square(img_surface)
    img_surface = invert_and_flatten_suface(img_surface)
    img_surface = blur_the_image(img_surface)
    return img_surface
