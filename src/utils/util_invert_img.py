#!/usr/bin/env python3
import sys
import numpy as np
import nibabel as nib

#def invert_img(input_file, output_file, scale_max=2048):
    ## Load NIfTI image
    #img = nib.load(input_file)
    #data = img.get_fdata()

    ## Scale to integer range [0, scale_max]
    #data_min = data.min()
    #data_max = data.max()

    #if data_max == data_min:
        #raise ValueError("Input image has constant intensity values.")

    #scaled = (data - data_min) / (data_max - data_min) * scale_max
    #scaled = np.round(scaled).astype(np.int32)

    ## Invert: max -> 0, min -> scale_max
    #inverted = scale_max - scaled

    ## Save back as NIfTI
    #new_img = nib.Nifti1Image(inverted, affine=img.affine, header=img.header)
    #nib.save(new_img, output_file)

def invert_img(input_file, output_file, scale_max=2048):
    # Load NIfTI image
    img = nib.load(input_file)
    data = img.get_fdata()

    # Make a mask of non-background voxels
    mask = data > 0

    if not np.any(mask):
        raise ValueError("Image has no nonzero voxels to invert.")

    # Scale only the nonzero intensities
    data_min = data[mask].min()
    data_max = data[mask].max()

    scaled = np.zeros_like(data, dtype=np.int32)
    scaled[mask] = np.round(
        (data[mask] - data_min) / (data_max - data_min) * scale_max
    ).astype(np.int32)

    # Invert nonzero voxels
    inverted = np.zeros_like(scaled, dtype=np.int32)
    inverted[mask] = scale_max - scaled[mask]

    # Save new image
    new_img = nib.Nifti1Image(inverted, affine=img.affine, header=img.header)
    nib.save(new_img, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python util_invert_image.py <input.nii.gz> <output.nii.gz>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    invert_img(input_file, output_file)


