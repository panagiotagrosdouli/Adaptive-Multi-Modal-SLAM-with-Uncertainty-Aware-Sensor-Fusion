import cv2
import numpy as np


def apply_motion_blur(image, ksize=9):
    if ksize <= 1:
        return image.copy()
    if ksize % 2 == 0:
        ksize += 1
    kernel = np.zeros((ksize, ksize), dtype=np.float32)
    kernel[ksize // 2, :] = 1.0 / ksize
    return cv2.filter2D(image, -1, kernel)


def reduce_brightness(image, scale=0.5):
    return np.clip(image.astype(np.float32) * scale, 0, 255).astype(np.uint8)


def add_gaussian_noise(image, sigma=10, seed=None):
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, sigma, image.shape)
    noisy = image.astype(np.float32) + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)


def drop_frame(image, drop=False):
    if drop:
        return np.zeros_like(image)
    return image.copy()


def degrade_image(
    image,
    brightness_scale=1.0,
    motion_blur_ksize=1,
    noise_sigma=0.0,
    drop=False,
    seed=None,
):
    degraded = image.copy()
    degraded = reduce_brightness(degraded, brightness_scale)
    degraded = apply_motion_blur(degraded, motion_blur_ksize)
    if noise_sigma > 0:
        degraded = add_gaussian_noise(degraded, noise_sigma, seed=seed)
    degraded = drop_frame(degraded, drop=drop)
    return degraded
