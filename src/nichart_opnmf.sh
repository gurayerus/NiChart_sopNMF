#!/usr/bin/bash +x
#
# ==========================================================
# Script: nichart_opnmf.sh
# Purpose: Compute ravens maps and extract opnmf values
# Author: Guray Erus
# Date: 2026-01-16
# ==========================================================
#
# Description:
#   This script calculates RAVENS maps and computes opnmf values
#
# Requirements:
#   - fireANTs or ANTs (>=2.0)
#   - bash
#
# Usage:
#   See usage
#
# ==========================================================

set -e

# Set number of threads for ANTs
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4

# Get absolute path to the folder containing this script
# SCRIPT_DIR="$(dirname "$(realpath "$0")")"
SCRIPT_DIR=$(pwd)
if [ -n "${BASH_SOURCE[0]}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    SCRIPT_DIR="$(pwd)"
fi
echo; echo "Script dir is: ${SCRIPT_DIR}"; echo;

# Define paths relative to the script location
RES_PATH="${SCRIPT_DIR}/../resources"

# ===============================
#   Usage and Help
# ===============================
usage() {
  echo
  echo "Usage: $0 --in_img <path> --in_seg <path> --labels <string> --out_dir <path> --out_prefix <string>"
  echo
  echo "Optional arguments:"
  echo "  --template <path>       Template image file (default: none)"
  echo "  --flag_invert <bool>    Whether to invert intensities (default: false)"
  echo "  --flag_del_tmp <bool>   Whether to delete temp output (default: false)"
  echo "  --label_dict <path>     ROI dictionary file (default: none)"
  echo "  --music_dir <path>      Music ROIs directory (default: none)"
  echo "  --reg_mode <str>        Registration mode (default: default)"
  echo "  --reg_backend <str>     Registration backend: ants | fireants (default: ants)"
  echo "  --icv_mask <int>        Mask to calculate intra-cranial volume (default: none)"
  echo
  echo "Example:"
  echo "  $0 --in_img subj01_T1.nii.gz --in_seg subj01_labels.nii.gz \\"
  echo "     --labels GM,WM --out_dir results --out_prefix subj01_ \\"
  echo "     --template template.nii.gz --music_dir ./refdata"
  echo "     --reg_mode test --icv_mask subj01_labels.nii.gz"
  echo
  exit 1
}

# ===============================
#   Parse Command-Line Arguments
# ===============================
# Default values
template="${RES_PATH}/templates/istaging/BLSA_SPGR+MPRAGE_averagetemplate.nii.gz"
label_dict="${RES_PATH}/dictionaries/list_MUSE_derived.csv"
reg_mode='default'
reg_backend='ants'

flag_invert='no'
flag_del_tmp='no'
icv_mask='none'


# Parse long options
while [[ $# -gt 0 ]]; do
  case "$1" in
    --in_img) in_img="$2"; shift 2;;
    --in_seg) in_seg="$2"; shift 2;;
    --labels) labels="$2"; shift 2;;
    --out_dir) out_dir="$2"; shift 2;;
    --out_prefix) out_prefix="$2"; shift 2;;
    --template) template="$2"; shift 2;;
    --flag_invert) flag_invert="$2"; shift 2;;
    --flag_del_tmp) flag_del_tmp="$2"; shift 2;;
    --flag_icvcorr) flag_icvcorr="$2"; shift 2;;
    --label_dict) label_dict="$2"; shift 2;;
    --music_dir) music_dir="$2"; shift 2;;
    --reg_mode) reg_mode="$2"; shift 2;;
    --reg_backend) reg_backend="$2"; shift 2;;
    --icv_mask) icv_mask="$2"; shift 2;;
    -h|--help) usage;;
    *) echo "Unknown option: $1"; usage;;
  esac
done

# ===============================
#   Validate Required Inputs
# ===============================
if [[ -z "$in_img" || -z "$in_seg" || -z "$labels" || -z "$out_dir" || -z "$out_prefix" ]]; then
  echo "Error: Missing one or more required arguments."
  usage
fi

# Invert template
if [[ "$flag_invert" == "yes" ]]; then
    if [[ "$template" != *_Inv.nii.gz ]]; then
        template="${template%.nii.gz}_Inv.nii.gz"
        echo "Warning: Template name should end with _Inv.nii.gz; renaming template"
    fi
fi

# ===============================
#   Check input files
# ===============================
if [ ! -f "$in_img" ]; then
    echo "Error: Input img does not exist: $in_img" >&2
    exit 1
fi
if [ ! -f "$in_seg" ]; then
    echo "Error: Input segmentation mask does not exist: $in_seg" >&2
    exit 1
fi
if [ ! -f "$template" ]; then
    echo "Error: Template image does not exist: $template" >&2
    exit 1
fi

flag_icvcorr='no'
if [ ! -z ${icv_mask} ]; then
    flag_icvcorr='yes'
fi

# ===============================
#   Prepare Output Directory
# ===============================
mkdir -p "$out_dir"

# ===============================
#   Run ravens calculation
# ===============================
echo "Running ravens calculation with the following parameters:"
echo "  in_img      = $in_img"
echo "  in_seg      = $in_seg"
echo "  labels      = $labels"
echo "  template    = $template"
echo "  out_dir     = $out_dir"
echo "  out_prefix  = $out_prefix"
echo "  flag_invert = $flag_invert"
echo "  label_dict  = $label_dict"
echo "  music_dir   = $music_dir"
echo "  reg_mode    = $reg_mode"
echo "  reg_backend = $reg_backend"
echo "  icv_mask    = $icv_mask"
echo "  flag_del_tmp = $flag_del_tmp"
echo "  music_dir = $music_dir"

echo

#-------------------------------
# --- Calculate RAVENS ---
if [ -e ${out_dir}/${out_prefix}_Label_GM_RAVENS.nii.gz ]; then
    echo "RAVENS map exists, skip ..."
else
    cmd="./calc_ravens_ants.sh --in_img ${in_img} --in_seg ${in_seg} --labels ${labels} --template ${template} --out_dir ${out_dir} --out_prefix ${out_prefix} --reg_mode ${reg_mode} --reg_backend ${reg_backend} --flag_invert ${flag_invert}"
    if [ ! -z ${label_dict} ]; then
        cmd="${cmd} --label_dict ${label_dict}"
    fi
    if [ ${flag_icvcorr} == 'yes' ]; then
        cmd="${cmd} --icv_mask ${icv_mask}"
    fi
    echo "About to run: $cmd"
    $cmd
fi

#-------------------------------
# --- Down sample ravens ---
in_img="${out_dir}/${out_prefix}Label_GM_RAVENS.nii.gz"
out_img="${out_dir}/${out_prefix}Label_GM_RAVENS_DS.nii.gz"
if [ -e ${out_img} ]; then
    echo "DS RAVENS map exists, skip: ${out_img}"
else
    cmd="3dresample -dxyz 2 2 2 -rmode Li -prefix ${out_img} -inset ${in_img}"
    echo "About to run: $cmd"
    $cmd
fi

#-------------------------------
# --- Calculate opNMF values ---
in_img="${out_dir}/${out_prefix}Label_GM_RAVENS_DS.nii.gz"
num_component='64'  
out_csv="${out_dir}/${out_prefix}MUSIC_C${num_component}.csv"
if [ -e ${out_csv} ]; then
    echo "MUSIC rois exist, skip ..."
else
    cmd="python utils/util_applyMusic.py --user_img ${in_img} --atlas_dir ${music_dir} --num_component 64 --out_csv ${out_csv}"
    echo "About to run: $cmd"
    $cmd    
fi

if [ "${flag_del_tmp}" == 'yes' ]; then
    echo; echo "Deleting temporary folders ..."

    rm -rf ${out_dir}/warps
    echo; echo "Removed temp folder: ${out_dir}/warps"
    
    rm -rf ${out_dir}/init
    echo; echo "Removed temp folder: ${out_dir}/init"
    
    rm -rf ${out_dir}/labels
    echo; echo "Removed temp folder: ${out_dir}/labels"

    rm -rf ${out_dir}/encoded
    echo; echo "Removed temp folder: ${out_dir}/encoded"

fi

