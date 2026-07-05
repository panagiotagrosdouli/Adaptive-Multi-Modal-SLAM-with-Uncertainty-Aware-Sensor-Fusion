from pathlib import Path

class EurocDataset:
    def __init__(self, root):
        self.root=Path(root)
        self.cam0=self.root/'mav0'/'cam0'/'data'
        self.cam1=self.root/'mav0'/'cam1'/'data'
        self.imu=self.root/'mav0'/'imu0'

    def image_files(self):
        return sorted(self.cam0.glob('*.png'))

    def __len__(self):
        return len(self.image_files())
