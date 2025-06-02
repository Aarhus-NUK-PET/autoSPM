import nibabel as nib
from totalsegmentator.python_api import totalsegmentator
import autoSPM.autoSPMwMask as spm
import os
import argparse

def autoSPM(imgPath, ctPath, outputPath=None, other=None, inter=None, verbose=False):
    """
    Main function to run the autoSPM pipeline.

    Parameters:
        imgPath (str): Path to the input image file.
        ctPath (str): Path to the CT image file.
        brainnum (int): Number of brain regions to segment.
        outputPath (str, optional): Path to save the output image. Defaults to None.
        other (optional): Additional imges to co-register (must be in MNI space).
        inter (optional): Interpolation method for co-registration of additional images in other.

    Returns:
        str: Path to the output image files.
    """
    if verbose: print("    ################ Running autoSPM ################  \n")
    spm.validate_inputs(imgPath, ctPath, outputPath, other, inter)
    segFile = os.path.join(outputPath, "brainSegmentation.nii")

    if verbose: print(f"    Running TotalSegmentator for brain segmentation on ct...")
    # Run TotalSegmentator for brain segmentation
    totalsegmentator(ctPath, segFile, roi_subset=['brain'], fast=True, verbose=verbose)
    if verbose: print(f"\n    TotalSegmentator finished! ")
    # Find the brain region number
    seg = nib.load(segFile)
    num = seg.get_fdata().max()
    if num == 0: raise ValueError("No brain region found in the segmentation file.")

    if verbose: print(f"\n    Running SPM registration...")

    registered = spm.autoSPMwMask(imgPath, segFile, brainnum=num, outputPath=outputPath, other=other, inter=inter, verbose=verbose)

    if verbose: print(f"\n    SPM registration finished!")
    if verbose: print(f"\n    ################ autoSPM finished! ################  \n")



def main():
    parser = argparse.ArgumentParser(description="Run autoSPM pipeline for brain segmentation and registration.")
    parser.add_argument("--toSegment", type=str, required=True, help="Path to the input image file.")
    parser.add_argument("--ctPath", type=str, required=True, help="Path to the CT image file.")
    parser.add_argument("--outputPath", type=str, default=None, help="Path to save the output image files.")
    parser.add_argument("--other", type=str, nargs='*', default=None, help="Additional images to co-register (must be in MNI space).")
    parser.add_argument("--inter", type=str, default=None, help="Interpolation method for co-registration of additional images.")
    parser.add_argument("--verbose", action='store_true', help="Enable verbose output.")

    args = parser.parse_args()
    
    autoSPM(args.toSegment, args.ctPath, args.outputPath, args.other, args.inter, args.verbose)


if __name__ == "__main__":
    main()
