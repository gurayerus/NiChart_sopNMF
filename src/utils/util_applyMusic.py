import argparse
import os
import math
import numpy as np
import pandas as pd
import nibabel as nib


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract ROI-wise mean and sum values from a NIfTI image using an atlas"
    )
    parser.add_argument(
        "--user_img",
        required=True,
        help="Path to the user NIfTI image (e.g., img.nii.gz)"
    )
    parser.add_argument(
        "--atlas_dir",
        required=True,
        help="Directory containing atlas NIfTI files"
    )
    parser.add_argument(
        "--num_component",
        type=int,
        required=True,
        help="Number of atlas components (e.g., 64)"
    )
    parser.add_argument(
        "--out_csv",
        required=True,
        help="Output CSV file path"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    user_img = args.user_img
    atlas_dir = args.atlas_dir
    num_component = args.num_component
    out_csv = args.out_csv

    # Construct atlas path
    atlas_path = os.path.join(atlas_dir, f"MuSIC_C{num_component}.nii.gz")

    # Load atlas
    atlas_img = nib.load(atlas_path)
    atlas_data = np.nan_to_num(atlas_img.get_fdata())

    # Load user image once (more efficient)
    user_img_nii = nib.load(user_img)
    user_data = np.nan_to_num(user_img_nii.get_fdata())

    results = {}

    # Loop over atlas components
    for i in range(1, num_component + 1):
        # Create mask for component i
        data_mask = atlas_data == i

        if np.sum(data_mask) == 0:
            results[f"component_{i}_mean"] = np.nan
            results[f"component_{i}_sum"] = np.nan
            continue

        masked_data = np.where(data_mask, user_data, 0)

        sum_value = np.sum(masked_data)
        mean_value = sum_value / np.sum(data_mask)

        if math.isnan(mean_value) or math.isnan(sum_value):
            results[f"component_{i}_mean"] = np.nan
            results[f"component_{i}_sum"] = np.nan
        else:
            results[f"component_{i}_mean"] = mean_value
            results[f"component_{i}_sum"] = sum_value

    # Convert to DataFrame and write CSV
    df_participant = pd.DataFrame([results])
    df_participant.to_csv(out_csv, index=False)


if __name__ == "__main__":
    main()

