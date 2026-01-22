#!/usr/bin/env python3
import nibabel as nib
import numpy as np
import sys
import pandas as pd

def read_roi_indices(label_list, dict_file=None):

    # Select labels from dictionary
    try:
        df = pd.read_csv(dict_file, header=None, dtype=str)
        df = df[df.iloc[:, 0].isin(label_list)]
    except:
        df = pd.DataFrame()

    # No dictionary or no match in dictionary, try to use each label as numeric index
    if df.shape[0] == 0:
        try:
            roi_dict = {x.strip(): int(x) for x in label_list}
        except:
            roi_dict = {}
            
    else:
        roi_dict = {}
        for _, row in df.iterrows():
            key = row[0]
            # Drop NaN, convert to int
            values = row[1:].dropna().astype(int).tolist()
            roi_dict[key] = values
        
    return roi_dict

def util_create_label_masks(seg_img, label_list, out_prefix, label_dict=None):
    """
    Create a binary mask for each label
    
    Args:
        seg_img (str): Path to segmentation image
        label_list (list of int or str): Labels to process
        out_prefix (str): Output prefix
        label_dict (list of int, optional): Label dict
    """
    # Load images
    seg_nii = nib.load(seg_img)

    seg_data = seg_nii.get_fdata()

    # Determine roi labels
    labels = [x for x in label_list.split(",")]
    roi_dict = read_roi_indices(labels, label_dict)
        
    if len(roi_dict) == 0:
        print("No target labels found!")
        return

    for roi, values in roi_dict.items():
        out_data = np.zeros_like(seg_data, dtype=np.uint8)
        out_data[np.isin(seg_data, values)] = 1
    
        out_nii = nib.Nifti1Image(out_data, affine=seg_nii.affine, header=seg_nii.header)
        out_fname = f"{out_prefix}{roi}.nii.gz"
        nib.save(out_nii, out_fname)
        print(f"Saved label {roi} to {out_fname}")
        
    # Save list of labels to file
    out_list = f'{out_prefix}List.csv'
    with open(out_list, "w") as f:
        for key in roi_dict.keys():
            f.write(f"{key}\n")    
    #np.savetxt(out_list, roi_dict.keys())
    print(f"Saved list of labels to {out_list}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create binary masks for labels")
    parser.add_argument("seg_img", help="Segmentation image (NIfTI)")
    parser.add_argument("labels", help="List of labels to process (e.g. 1,2 or GM,WM)")
    parser.add_argument("out_prefix", help="Output prefix")
    parser.add_argument("--label_dict", default=None, help="Label dictionary to detect indices for labels (default: not used)")

    args = parser.parse_args()

    util_create_label_masks(args.seg_img, args.labels, args.out_prefix, args.label_dict)
