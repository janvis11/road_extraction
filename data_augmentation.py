class RoadDataset(Dataset):
    def __init__(self, img_dir, mask_dir, mean, std, augment=False):
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.images = list_tifs(img_dir)
        self.augment = augment

        self.mean = mean
        self.std = std

        if len(self.images) == 0:
            raise RuntimeError(f"No tif images found in {img_dir}")

        sample_img_path = os.path.join(self.img_dir, self.images[0])
        with rasterio.open(sample_img_path) as src:
            self.raw_band_count = src.count

        self.out_channels = 5 if self.raw_band_count >= 4 else 3

        if self.augment:
            self.transform = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.5),
                A.RandomRotate90(p=0.5),
                A.Transpose(p=0.2),
                A.ShiftScaleRotate(
                    shift_limit=0.03,
                    scale_limit=0.05,
                    rotate_limit=10,
                    interpolation=cv2.INTER_LINEAR,
                    border_mode=cv2.BORDER_REFLECT_101,
                    p=0.4
                ),
                A.RandomBrightnessContrast(
                    brightness_limit=0.15,
                    contrast_limit=0.15,
                    p=0.3
                ),
                A.GaussNoise(
                    std_range=(0.01, 0.05),
                    mean_range=(0.0, 0.0),
                    p=0.2
                ),
            ])
        else:
            self.transform = None

        print(f"Dataset: {img_dir}")
        print(f"Channels: {self.out_channels}")
        print(f"Augment: {self.augment}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_name = self.images[idx]
        img_path = os.path.join(self.img_dir, img_name)

        mask_name = expected_mask_name_from_image(img_name)
        mask_path = os.path.join(self.mask_dir, mask_name)

        with rasterio.open(img_path) as src:
            image = src.read().transpose(1, 2, 0).astype(np.float32)

        with rasterio.open(mask_path) as src:
            mask = src.read(1).astype(np.float32)

        image, _ = compute_input_features(image)

        # ✅ APPLY DATASET NORMALIZATION HERE
        image = (image - self.mean) / self.std

        mask = (mask > 0).astype(np.float32)

        if self.transform is not None:
            augmented = self.transform(image=image, mask=mask)
            image = augmented["image"]
            mask = augmented["mask"]

        image = torch.from_numpy(image).permute(2, 0, 1).float()
        mask  = torch.from_numpy(mask).unsqueeze(0).float()

        return image, mask