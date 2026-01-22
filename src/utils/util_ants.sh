#!/usr/bin/bash +x
#
# ==========================================================
# Script: util_ants.sh
# Purpose: Functions to run and apply ANTs
# Author: Guray Erus
# Date: 2025-08-25
# ==========================================================
#
# Requirements:
#   - ANTs (>=2.0)
#   - bash
#
# Usage:
#   Source the script and call functions
#
# ==========================================================

set -euo pipefail

ants_reg() {
  # Runs ANTs using various profiles
  #
  # Profiles:
  #
  # - default_script: Default version using ANTs script "antsRegistrationSyN.sh"
  #
  # - default: Replicates parameters in "antsRegistrationSyN.sh"
  #   -- Provided to show specific parameters used in default ANTs script
  #   -- Runs 4 iteration levels. The most time consuming part is the 4th level of 
  #      deformable registration (transform: Syn, convergence: 1000x70x50x20)
  #      e.g. 4th level is iterated 20 times and each iteration takes couple of minutes
  #
  # - quick_script: Quick version using ANTs script "antsRegistrationSyNQuick.sh"
  #
  # - quick: Replicates parameters in "antsRegistrationSyNQuick.sh"
  #   -- Similar to default version; except iteration # at 4th level is set to 0, so it's skipped
  #
  # - balanced: Parameters set to run it faster without penalizing accuracy too much
  #
  # - test: Very fast version for testing the pipeline. Results will not be accurate
  #
  
  local profile="$1"
  local fixed="$2"
  local moving="$3"
  local outprefix="$4"

  # Choose options based on profile
  case "$profile" in
    default_script)
      cmd=(antsRegistrationSyN.sh
        -d 3
        -f "$fixed"
        -m "$moving"
        -o "$outprefix"
      )
      ;;
    default)
      cmd=(antsRegistration
        --verbose 1
        --dimensionality 3 
        --float 0
        --collapse-output-transforms 1
        --output ["${outprefix}",${outprefix}Warped.nii.gz,${outprefix}InwerseWarped.nii.gz]
        --interpolation Linear
        --use-histogram-matching 0
        --winsorize-image-intensities [0.005,0.995] 
        --initial-moving-transform ["$fixed","$moving",1]
        --transform Rigid[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [1000x500x250x100,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox
        --transform Affine[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [1000x500x250x100,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox          
        --transform SyN[0.1,3,0]
          --metric CC["$fixed","$moving",1,4]
          --convergence [100x70x50x20,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox
      )
      ;;
    quick_script)   
      cmd=(antsRegistrationSyNQuick.sh
        -d 3
        -f "$fixed"
        -m "$moving"
        -o "$outprefix"
      )
      ;;
    quick)
      cmd=(antsRegistration
        --verbose 1
        --dimensionality 3 
        --float 0
        --collapse-output-transforms 1
        --output ["${outprefix}",${outprefix}Warped.nii.gz,${outprefix}InwerseWarped.nii.gz]
        --interpolation Linear
        --use-histogram-matching 0
        --winsorize-image-intensities [0.005,0.995] 
        --initial-moving-transform ["$fixed","$moving",1]
        --transform Rigid[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [1000x500x250x0,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox
        --transform Affine[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [1000x500x250x0,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox          
        --transform SyN[0.1,3,0]
          --metric CC["$fixed","$moving",1,4]
          --convergence [100x70x50x0,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox
      )
      ;;
    balanced)
      cmd=(antsRegistration
        --verbose 1
        --dimensionality 3 
        --float 0
        --collapse-output-transforms 1
        --output ["${outprefix}",${outprefix}Warped.nii.gz,${outprefix}InwerseWarped.nii.gz]
        --interpolation Linear
        --use-histogram-matching 0
        --winsorize-image-intensities [0.005,0.995] 
        --initial-moving-transform ["$fixed","$moving",1]
        --transform Rigid[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [10x50x50x10,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox
        --transform Affine[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [10x50x50x10,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox          
        --transform SyN[0.1,3,0]
          --metric CC["$fixed","$moving",1,4]
          --convergence [10x50x50x10,1e-6,10]
          --shrink-factors 8x4x2x1
          --smoothing-sigmas 3x2x1x0vox
      )
      ;;      
    test)
      cmd=(antsRegistration
        --dimensionality 3 
        --float 1
        --output ["${outprefix}",${outprefix}Warped.nii.gz]
        --interpolation Linear
        --use-histogram-matching 0
        --collapse-output-transforms 1        
        --verbose 1        
        --initial-moving-transform ["$fixed","$moving",1]
        --transform Rigid[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [8x2x0,1e-6,10]
          --shrink-factors 4x2x1
          --smoothing-sigmas 2x1x0vox
        --transform Affine[0.1]
          --metric MI["$fixed","$moving",1,32,Regular,0.25]
          --convergence [8x2x0,1e-6,10]
          --shrink-factors 4x2x1
          --smoothing-sigmas 2x1x0vox          
        --transform SyN[0.25,3,0]
          --metric CC["$fixed","$moving",1,4]
          --convergence [8x2x0,1e-6,10]
          --shrink-factors 4x2x1
          --smoothing-sigmas 2x1x0vox
      )
      ;;
    *)
      echo "Usage: ants_reg {default_script|default|quick_script|quick|balanced|test} fixed.nii.gz moving.nii.gz outprefix pval"
      return 1
      ;;
  esac

  # Print nicely
  echo; echo ">>> Command to run:"
  printf '%s ' "${cmd[@]}"
  echo -e "\n"

  # Run
  "${cmd[@]}"
}

ants_apply() {
    local s_file="$1"
    local in_def="$2"
    local t_file="$3"
    local interp="$4"
    local out_warped="$5"
    
    if [ "$interp" == 'NearestNeighbor' ]; then
        cmd=(WarpImageMultiTransform 3
            ${s_file}
            ${out_warped}
            -R ${t_file}
            --use-NN
            ${in_def}
        )
    else
        cmd=(WarpImageMultiTransform 3
            ${s_file}
            ${out_warped}
            -R ${t_file}
            ${in_def}
        )
    fi

    # Print nicely
    echo; echo ">>> Command to run:"
    printf '%s ' "${cmd[@]}"
    echo -e "\n"

    # Run
    "${cmd[@]}"
}
      
ants_calc_jacdet() {
    local in_def="$1"
    local out_jac="$2"

    cmd=(CreateJacobianDeterminantImage 3 ${in_def} ${out_jac})

    # Print nicely
    echo; echo ">>> Command to run:"
    printf '%s ' "${cmd[@]}"
    echo -e "\n"

    # Run
    "${cmd[@]}"
}
  
ants_compose() {
    local in_warp="$1"
    local in_affine="$2"
    local t_file="$3"
    local out_def="$4"

    cmd=(ComposeMultiTransform 3 
         ${out_def}
         -R ${t_file}
         ${in_warp}
         ${in_affine}
    )

    # Print nicely
    echo; echo ">>> Command to run:"
    printf '%s ' "${cmd[@]}"
    echo -e "\n"

    # Run
    "${cmd[@]}"
}

ants_apply_inv() {
    local in_map="$1"
    local in_img="$2"
    local in_warp="$3"
    local in_affine="$4"
    local out_map="$5"
    local interp="$6"
    
    # ---------------------------
    # Check required args
    # ---------------------------
    if [ -z "${in_map:-}" ] || [ -z "${in_img:-}" ] || [ -z "${in_warp:-}" ] || [ -z "${in_affine:-}" ]; then
        echo "Error: Missing required argument(s)."
        usage
    fi

    # ---------------------------
    # Build antsApplyTransforms command
    # ---------------------------
    cmd=(antsApplyTransforms -d 3
        -i "${in_map}"
        -r "${in_img}"
        -n "${interp}"
        -o "${out_map}"
        -t "[${in_affine},1]"
        -t "${in_warp}"     
        )

#     # ---------------------------
#     # Run
#     # ---------------------------
#     echo "Running: ${cmd[*]}"
#     "${cmd[@]}"

    # Print nicely
    echo; echo ">>> Command to run:"
    printf '%s ' "${cmd[@]}"
    echo -e "\n"

    # Run
    "${cmd[@]}"
}


