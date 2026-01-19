import numpy as np
from scipy.ndimage import gaussian_filter # type: ignore
from PIL import Image, ImageFilter
from typing import Generator
from dataclasses import dataclass


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
    img = img / 400.0 # we flatten the height map
    return img

def blur_the_image(img: np.ndarray) -> np.ndarray:
    SIGMA = 1.8
    return gaussian_filter(img, sigma=SIGMA) # type: ignore

def _get_parabaloid_mask(H: int, W: int) -> np.ndarray:
    y = np.linspace(0, 1, H)
    x = np.linspace(0, 1, W)
    Y, X = np.meshgrid(y, x, indexing="ij")

    a = 1
    b = 0.5
    m = 0.55
    n = 0.5
    h = 0.5
    x_shift = X - m
    y_shift = Y - n
    return a * (x_shift ** 2) + b * (y_shift ** 2) + h

def normalize_array(arr: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    max_val = arr.max()
    return arr / (max_val + eps)

def apply_deadzone_mask(img: np.ndarray) -> np.ndarray:
    para_mask = _get_parabaloid_mask(*img.shape)
    para_mask = normalize_array(para_mask)
    return img * para_mask

def get_grads_np(img: np.ndarray):
    """
    return the gradient assuming z: f(x, y) -> img where x, y in [0, 1]
    """
    H, W = img.shape
    assert H == W
    spacing = 1 / H
    gradient_y, gradient_x = np.gradient(img, spacing)
    return gradient_x, gradient_y  # keep same convention as your torch version

def run_simulation(gradient_x, gradient_y, start_coords):
    ...

def process_image(img: Image.Image) -> np.ndarray:
    # Pre-processing
    img = convert_to_greyscale(img)
    img_surface = convert_to_numpy(img)
    img_surface = center_crop_square(img_surface)
    img_surface = invert_and_flatten_suface(img_surface)
    img_surface = blur_the_image(img_surface)
    img_surface = apply_deadzone_mask(img_surface)

    gradient_x, gradient_y = get_grads_np(img_surface)


    return img_surface

