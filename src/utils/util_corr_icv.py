#!/usr/bin/env python3
import sys
import numpy as np
import nibabel as nib
import os

def corr_icv(input_file, icvmask_file, output_file, MEAN_ICV=1450000):
    # Load NIfTI image
    nii = nib.load(input_file)
    data = nii.get_fdata()

    # Calculate icv
    nii_icv = nib.load(icvmask_file)
    img_icv = nii_icv.get_fdata()
    vox_dims = nii_icv.header.get_zooms()[:3]
    vox_vol = np.prod(vox_dims)
    n_voxels = np.count_nonzero(img_icv )
    icv = n_voxels * vox_vol

    # Correct icv
    data = data * MEAN_ICV / icv

    # Save new image
    new_img = nib.Nifti1Image(data, affine=nii.affine, header=nii.header)
    nib.save(new_img, output_file)

    # Save icv
    output_txt = os.path.join(os.path.dirname(output_file), 'icv_volume.csv')
    with open(output_txt, "w") as f:
        f.write(f"{icv}\n")
    
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python util_corr_icv.py <input.nii.gz> <icvmask.nii.gz> <output.nii.gz>")
        sys.exit(1)

    input_file = sys.argv[1]
    icvmask_file = sys.argv[2]
    output_file = sys.argv[3]

    corr_icv(input_file, icvmask_file, output_file)


