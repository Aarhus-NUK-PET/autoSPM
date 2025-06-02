import nibabel as nib
from totalsegmentator.python_api import totalsegmentator
import autoSPM as spm
import os
import argparse

def autoSPM(imgPath, ctPath, outputPath=None, other=None, inter=None, verbose=False, fullverbose=False):
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
    if fullverbose: verbose = True
    if verbose: print("################ Running autoSPM ################  \n")
    spm.validate_inputs(imgPath, ctPath, outputPath, other, inter)

    if verbose: print(f"Running TotalSegmentator for brain segmentation on ct...")
    # Run TotalSegmentator for brain segmentation
    if not 'brain.nii.gz' in os.listdir(outputPath):
        totalsegmentator(ctPath, outputPath, roi_subset=['brain'], fast=True, fullverbose=fullverbose)
        if verbose: print(f"TotalSegmentator finished! ")
    else: 
        if verbose: print(f"Brain mask found, skipping segmentation.")
    # Find the brain region number
    segFile = os.path.join(outputPath, 'brain.nii.gz')
    seg = nib.load(segFile)
    num = seg.get_fdata().max().astype(int)
    if num == 0: raise ValueError("No brain region found in the segmentation file.")

    if verbose: print(f"\nRunning SPM registration...")

    registered = spm.autoSPMwMask(imgPath, segFile, brainnum=int(num), outputPath=outputPath, other=other, inter=inter, verbose=verbose)

    if verbose: print(f"\nSPM registration finished!")
    if verbose: print(f"\n################ autoSPM finished! ################  \n")



def main():
    parser = argparse.ArgumentParser(description="Run autoSPM pipeline for brain segmentation and registration.")
    parser.add_argument("--toSegment", type=str, required=True, help="Path to the input image file.")
    parser.add_argument("--ctPath", type=str, required=True, help="Path to the CT image file.")
    parser.add_argument("--outputPath", type=str, default=None, help="Path to save the output image files.")
    parser.add_argument("--other", type=str, nargs='*', default=None, help="Additional images to co-register (must be in MNI space).")
    parser.add_argument("--inter", type=str, default=None, help="Interpolation method for co-registration of additional images.")
    parser.add_argument("--verbose", action='store_true', help="Enable verbose output.")
    parser.add_argument("--fullverbose", action='store_true', help="Enable full verbose output for TotalSegmentator.")

    args = parser.parse_args()
    
    autoSPM(args.toSegment, args.ctPath, args.outputPath, args.other, args.inter, args.verbose, args.fullverbose)


if __name__ == "__main__":
    main()
