from src.dataset_loader import EurocDataset


def main():
    dataset = EurocDataset('data/EuRoC')
    print(f'Frames available: {len(dataset)}')
    print('Experiment pipeline initialized.')


if __name__ == '__main__':
    main()
