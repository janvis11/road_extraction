def expected_mask_name_from_image(img_name):
    stem = img_name[:-4]
    parts = stem.split("_")

    if len(parts) != 3:
        raise ValueError(
            f"Unexpected image name format: {img_name}. Expected city_row_col.tif"
        )

    city, row, col = parts
    return f"{city}_mask_{row}_{col}.tif"


def compute_input_features(image_hwc):
    """
    Returns raw features (NO normalization here)

    Output:
    - 5 channels if NIR exists: [R, G, B, NDVI, NDWI]
    - 3 channels otherwise: [R, G, B]
    """
    image_hwc = image_hwc.astype(np.float32)
    c = image_hwc.shape[-1]

    rgb = image_hwc[:, :, :3].astype(np.float32)

    if c >= 4:
        r   = image_hwc[:, :, 0]
        g   = image_hwc[:, :, 1]
        b   = image_hwc[:, :, 2]
        nir = image_hwc[:, :, 3]

        eps = 1e-6
        ndvi = (nir - r) / (nir + r + eps)
        ndwi = (g - nir) / (g + nir + eps)

        feat = np.concatenate(
            [rgb, ndvi[..., None], ndwi[..., None]],
            axis=-1
        ).astype(np.float32)

        return feat, True

    return rgb.astype(np.float32), False



def compute_dataset_stats(img_dir, max_samples=200):
    image_files = list_tifs(img_dir)
    image_files = image_files[:max_samples]  # speed-up (optional)

    channel_sum = None
    channel_sq_sum = None
    pixel_count = 0

    for img_name in image_files:
        img_path = os.path.join(img_dir, img_name)

        with rasterio.open(img_path) as src:
            image = src.read().transpose(1, 2, 0).astype(np.float32)

        feat, _ = compute_input_features(image)  # NO normalization

        h, w, c = feat.shape
        feat = feat.reshape(-1, c)

        if channel_sum is None:
            channel_sum = feat.sum(axis=0)
            channel_sq_sum = (feat ** 2).sum(axis=0)
        else:
            channel_sum += feat.sum(axis=0)
            channel_sq_sum += (feat ** 2).sum(axis=0)

        pixel_count += feat.shape[0]

    mean = channel_sum / pixel_count
    std = np.sqrt(channel_sq_sum / pixel_count - mean ** 2)

    std[std < 1e-6] = 1.0

    print("Dataset mean:", mean)
    print("Dataset std :", std)

    return mean.astype(np.float32), std.astype(np.float32)

DATA_MEAN, DATA_STD = compute_dataset_stats(TRAIN_IMG)