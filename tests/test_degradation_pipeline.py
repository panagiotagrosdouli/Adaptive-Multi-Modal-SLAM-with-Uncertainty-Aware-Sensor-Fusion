import numpy as np

from scripts.degradation_pipeline import (
    add_gaussian_noise,
    apply_motion_blur,
    degrade_image,
    drop_frame,
    reduce_brightness,
)


def test_reduce_brightness_scales_pixel_values():
    image = np.full((4, 4), 100, dtype=np.uint8)
    degraded = reduce_brightness(image, scale=0.5)
    assert degraded.mean() == 50


def test_motion_blur_preserves_shape():
    image = np.zeros((5, 5), dtype=np.uint8)
    image[2, 2] = 255
    degraded = apply_motion_blur(image, ksize=3)
    assert degraded.shape == image.shape


def test_gaussian_noise_is_seeded_and_reproducible():
    image = np.full((4, 4), 100, dtype=np.uint8)
    first = add_gaussian_noise(image, sigma=5, seed=1)
    second = add_gaussian_noise(image, sigma=5, seed=1)
    assert np.array_equal(first, second)


def test_drop_frame_returns_black_image():
    image = np.full((4, 4), 100, dtype=np.uint8)
    dropped = drop_frame(image, drop=True)
    assert dropped.sum() == 0


def test_degrade_image_combines_operations():
    image = np.full((4, 4), 100, dtype=np.uint8)
    degraded = degrade_image(
        image,
        brightness_scale=0.5,
        motion_blur_ksize=1,
        noise_sigma=0,
        drop=False,
    )
    assert degraded.mean() == 50
