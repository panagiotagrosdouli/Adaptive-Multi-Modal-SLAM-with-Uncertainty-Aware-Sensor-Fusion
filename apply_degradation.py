import argparse
from pathlib import Path

import cv2

from scripts.degradation_pipeline import degrade_image


def parse_args():
    parser = argparse.ArgumentParser(description='Apply controlled degradations to an image sequence.')
    parser.add_argument('--input-dir', required=True, help='Directory containing input images.')
    parser.add_argument('--output-dir', required=True, help='Directory where degraded images will be written.')
    parser.add_argument('--brightness-scale', type=float, default=1.0)
    parser.add_argument('--motion-blur-ksize', type=int, default=1)
    parser.add_argument('--noise-sigma', type=float, default=0.0)
    parser.add_argument('--drop-every-n', type=int, default=0, help='Set every Nth frame to black. Disabled if 0.')
    parser.add_argument('--seed', type=int, default=0)
    return parser.parse_args()


def iter_images(input_dir):
    input_dir = Path(input_dir)
    extensions = ('*.png', '*.jpg', '*.jpeg')
    image_paths = []
    for extension in extensions:
        image_paths.extend(input_dir.glob(extension))
    return sorted(image_paths)


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = iter_images(args.input_dir)
    for index, image_path in enumerate(image_paths):
        image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        if image is None:
            continue

        drop = args.drop_every_n > 0 and (index + 1) % args.drop_every_n == 0
        degraded = degrade_image(
            image,
            brightness_scale=args.brightness_scale,
            motion_blur_ksize=args.motion_blur_ksize,
            noise_sigma=args.noise_sigma,
            drop=drop,
            seed=args.seed + index,
        )
        cv2.imwrite(str(output_dir / image_path.name), degraded)

    print(f'Processed images: {len(image_paths)}')
    print(f'Output directory: {output_dir}')


if __name__ == '__main__':
    main()
