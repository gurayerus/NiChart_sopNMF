#!/usr/bin/env python3
import sys
import numpy as np
import nibabel as nib
import os

def mask_image(input_file, mask_file, output_file):
    # Load NIfTI image
    nii = nib.load(input_file)
    data = nii.get_fdata()

    # Load mask image
    nii_mask = nib.load(mask_file)
    img_mask = nii_mask.get_fdata()

    # Apply mask
    data[img_mask <= 0] = 0

    # Save new image
    new_img = nib.Nifti1Image(data, affine=nii.affine, header=nii.header)
    nib.save(new_img, output_file)
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python mask_img.py <input.nii.gz> <mask.nii.gz> <output.nii.gz>")
        sys.exit(1)

    input_file = sys.argv[1]
    mask_file = sys.argv[2]
    output_file = sys.argv[3]

    mask_image(input_file, mask_file, output_file)


