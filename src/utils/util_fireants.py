#!/usr/bin/env python3
"""
Utility functions to run registration with FireANTs in the NiChart_RAVENS pipeline.

This script is intended to mirror the role of the ANTs-based helper in
`util_ants.sh` for the **registration step only**:

- It computes an affine + deformable registration between a fixed (template)
  image and a moving (subject) image using FireANTs.
- It saves:
    * the moved image in fixed space: ``<out_prefix>Warped.nii.gz``
    * a forward deformation field in ANTs-compatible format: ``<out_prefix>Def.nii.gz``
    * an inverse deformation field in ANTs-compatible format: ``<out_prefix>InvDef.nii.gz``

The resulting deformation fields can then be consumed by the existing ANTs-based
utilities (`CreateJacobianDeterminantImage`, `WarpImageMultiTransform`,
`antsApplyTransforms`, etc.) in the shell scripts.

Usage (CLI):
    python3 utils/util_fireants.py \\
        --fixed <template.nii.gz> \\
        --moving <t1_icv.nii.gz> \\
        --out_prefix /path/to/warps/prefix \\
        --profile <default|quick|balanced|test>
"""

import argparse
import os
from typing import Tuple

from fireants.io import Image, BatchedImages, FakeBatchedImages
from fireants.registration.affine import AffineRegistration
from fireants.registration.moments import MomentsRegistration
from fireants.registration.greedy import GreedyRegistration


def _get_profile_params(profile: str) -> Tuple[Tuple[int, ...], Tuple[int, ...], float, float]:
    """
    Map a registration profile name to FireANTs multi-scale parameters.

    Returns:
        (scales, iterations, affine_lr, deform_lr)
    """
    profile = profile.lower()

    if profile == "test":
        # Very fast / low accuracy
        scales = (4, 2, 1)
        iterations = (8, 2, 0)
        affine_lr = 3e-3
        deform_lr = 0.5
    elif profile == "quick":
        # Faster than default
        scales = (4, 2, 1)
        iterations = (100, 50, 0)
        affine_lr = 3e-3
        deform_lr = 0.5
    elif profile == "balanced":
        # Balanced speed/accuracy
        scales = (4, 2, 1)
        iterations = (50, 50, 25)
        affine_lr = 3e-3
        deform_lr = 0.5
    else:
        # "default" and any unknown value fall back here
        scales = (4, 2, 1)
        iterations = (200, 100, 50)
        affine_lr = 3e-3
        deform_lr = 0.5

    return scales, iterations, affine_lr, deform_lr


def run_fireants_registration(
    fixed_path: str,
    moving_path: str,
    out_prefix: str,
    profile: str = "default",
    do_moments: bool = True,
) -> None:
    """
    Run affine + greedy deformable registration with FireANTs.

    Args:
        fixed_path: Path to fixed (template) image.
        moving_path: Path to moving (subject/T1) image.
        out_prefix: Path prefix for outputs (directory + prefix stem).
            For example, if out_prefix="/tmp/warps/subj1_", this will write:
                /tmp/warps/subj1_Warped.nii.gz
                /tmp/warps/subj1_Def.nii.gz
                /tmp/warps/subj1_InvDef.nii.gz
        profile: Registration profile name.
    """
    scales, iterations, affine_lr, deform_lr = _get_profile_params(profile)

    # Load images
    fixed_img = Image.load_file(fixed_path)
    moving_img = Image.load_file(moving_path)

    fixed_batch = BatchedImages([fixed_img])
    moving_batch = BatchedImages([moving_img])

    init_rigid = None

    # -----------------------------
    # Moments registration (initial alignment)
    # -----------------------------
    if do_moments:
        moments = MomentsRegistration(
            scale=1.0,
            fixed_images=fixed_batch,
            moving_images=moving_batch,
            moments=2,
            orientation="rot",
            blur=False,
            loss_type="fusedcc",
            cc_kernel_type="rectangular",
            cc_kernel_size=5,
        )
        print(f"[FireANTs] Running moments initialization (profile='{profile}')")
        moments.optimize()
        init_rigid = moments.get_affine_init().detach()

        # Save moments initialization transform in ANTs format (debuggable, and useful for parity with tutorial)
        moments_path = f"{out_prefix}MomentsInit.mat"
        print(f"[FireANTs] Writing moments init transform (ANTs format) to: {moments_path}")
        moments.save_as_ants_transforms(moments_path)

        # Save moments-warped (resliced) image (optional but helpful for debugging)
        moved_moments = moments.evaluate(fixed_batch, moving_batch)
        moved_moments_batch = FakeBatchedImages(moved_moments, fixed_batch)
        moved_moments_path = f"{out_prefix}MomentsWarped.nii.gz"
        print(f"[FireANTs] Writing moments-warped image to: {moved_moments_path}")
        moved_moments_batch.write_image(moved_moments_path)

    # -----------------------------
    # Affine registration
    # -----------------------------
    affine = AffineRegistration(
        scales=list(scales),
        iterations=list(iterations),
        fixed_images=fixed_batch,
        moving_images=moving_batch,
        init_rigid=init_rigid,
        loss_type="cc",
        optimizer="Adam",
        optimizer_lr=affine_lr,
        cc_kernel_size=5,
    )
    print(f"[FireANTs] Running affine registration with profile='{profile}'")
    affine.optimize()
    init_affine = affine.get_affine_matrix().detach()

    # Save affine transform in ANTs-compatible format (used for consistency with ANTs outputs)
    affine_path = f"{out_prefix}0GenericAffine.mat"
    print(f"[FireANTs] Writing affine transform (ANTs format) to: {affine_path}")
    affine.save_as_ants_transforms([affine_path])

    # -----------------------------
    # Deformable (Greedy) registration
    # -----------------------------
    # Mirror tutorial1 defaults: keep last (finest) stage shorter for deformable
    deform_iterations = list(iterations)
    if len(deform_iterations) >= 3 and deform_iterations[-1] > 25:
        deform_iterations[-1] = 25

    reg = GreedyRegistration(
        scales=list(scales),
        iterations=deform_iterations,
        fixed_images=fixed_batch,
        moving_images=moving_batch,
        cc_kernel_size=5,
        deformation_type="compositive",
        optimizer="Adam",
        optimizer_lr=deform_lr,
        smooth_grad_sigma=0.5,
        # smooth_warp_sigma=0.0,
        init_affine=init_affine,
    )

    print(f"[FireANTs] Running deformable registration with profile='{profile}'")
    reg.optimize()

    # -----------------------------
    # Save moved image in fixed space
    # -----------------------------
    moved = reg.evaluate(fixed_batch, moving_batch)
    moved_batch = FakeBatchedImages(moved, fixed_batch)

    moved_path = f"{out_prefix}Warped.nii.gz"
    print(f"[FireANTs] Writing moved image to: {moved_path}")
    moved_batch.write_image(moved_path)

    # -----------------------------
    # Save forward & inverse warps in ANTs-compatible format
    # -----------------------------
    forward_warp_path = f"{out_prefix}Def.nii.gz"
    inverse_warp_path = f"{out_prefix}InvDef.nii.gz"

    print(f"[FireANTs] Writing forward deformation (ANTs format) to: {forward_warp_path}")
    reg.save_as_ants_transforms([forward_warp_path], save_inverse=False)

    print(f"[FireANTs] Writing inverse deformation (ANTs format) to: {inverse_warp_path}")
    reg.save_as_ants_transforms([inverse_warp_path], save_inverse=True)


def main():
    parser = argparse.ArgumentParser(
        description="Run FireANTs registration and export ANTs-compatible transforms."
    )
    parser.add_argument(
        "--fixed",
        required=True,
        help="Fixed (template) image path (NIfTI).",
    )
    parser.add_argument(
        "--moving",
        required=True,
        help="Moving (subject) image path (NIfTI).",
    )
    parser.add_argument(
        "--out_prefix",
        required=True,
        help=(
            "Output prefix (directory + prefix). "
            "Example: /path/to/warps/subj1_"
        ),
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="Registration profile: default | quick | balanced | test (default: default).",
    )
    parser.add_argument(
        "--no-moments",
        action="store_true",
        help="Disable moments initialization (default: moments enabled).",
    )

    args = parser.parse_args()

    fixed = os.path.abspath(args.fixed)
    moving = os.path.abspath(args.moving)
    out_prefix = os.path.abspath(args.out_prefix)

    run_fireants_registration(
        fixed_path=fixed,
        moving_path=moving,
        out_prefix=out_prefix,
        profile=args.profile,
        do_moments=not args.no_moments,
    )


if __name__ == "__main__":
    main()


