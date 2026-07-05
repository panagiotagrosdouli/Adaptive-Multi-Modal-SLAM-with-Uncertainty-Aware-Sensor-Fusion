import cv2
import numpy as np


def apply_motion_blur(image, ksize=9):
    kernel = np.zeros((ksize, ksize), dtype=np.float32)
    kernel[ksize // 2, :] = 1.0 / ksize
    return cv2.filter2D(image, -1, kernel)


def reduce_brightness(image, scale=0.5):
    return np.clip(image.astype(np.float32) * scale, 0, 255).astype(np.uint8)


def add_gaussian_noise(image, sigma=10):
    noise = np.random.normal(0, sigma, image.shape)
    noisy = image.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)
