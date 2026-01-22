#!/usr/bin/env python3
import nibabel as nib
import numpy as np
import sys

def util_multiply_images(img1, img2, out_img):
    """
    Multiply two images voxelwise.
    
    Args:
        img1 (str): Path to image 1
        img2 (str): Path to image 2
        out_img (str): Output image
    """
    # Load images
    img1_nii = nib.load(img1)
    img2_nii = nib.load(img2)

    img1_data = img1_nii.get_fdata()
    img2_data = img2_nii.get_fdata()

    if img1_data.shape != img2_data.shape:
        raise ValueError("Img1 and Img2 images must have the same shape")

    out_data = img1_data * img2_data

    out_nii = nib.Nifti1Image(out_data, affine=img1_nii.affine, header=img1_nii.header)
    nib.save(out_nii, out_img)
    print(f"Saved output to {out_img}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multiply two images voxelwise")
    parser.add_argument("img1", help="Image1 (NIfTI)")
    parser.add_argument("img2", help="Image2 (NIfTI)")
    parser.add_argument("out_img", help="Output image")

    args = parser.parse_args()

    util_multiply_images(args.img1, args.img2, args.out_img)
