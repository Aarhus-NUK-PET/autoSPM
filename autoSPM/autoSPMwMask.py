import os
import numpy as np
from scipy.ndimage import binary_dilation
import SimpleITK as sitk
import matlab.engine
import sys



def autoSPMwMask(imgPath, maskPath, brainnum=1, outputPath=None, filename='Brain', toSpace='MNI', norm=True, other=None, inter=None, verbose=False):
    """
    Saves 
    
    Parameters:
    spm_path (str): Path to the SPM installation directory.
    mask_path (str): Path to the input mask file.
    output_path (str, optional): Path to save the output white matter mask. If None, uses default path.
    
    Returns:
    str: Path to the generated white matter mask.
    """
    validate_inputs(imgPath=imgPath, maskPath=maskPath, toSpace=toSpace, norm=norm, outputPath=outputPath, filename=filename, other=other, inter=inter)
    validate_brainnum(maskPath, brainnum)
    toSpace = toSpace.lower()
    
    # Start MATLAB engine
    eng = matlab.engine.start_matlab()
    currDir = os.path.dirname(os.path.abspath(__file__))
    eng.addpath(currDir, nargout=0)

    # Image load and resampling
    img = imgLoad(imgPath)
    mask = imgLoad(maskPath)
    maskResamp = sitk.Resample(mask, img, sitk.Transform(), sitk.sitkNearestNeighbor,
                               0, mask.GetPixelID())
    maskArr = sitk.GetArrayFromImage(maskResamp)
    imgArr = sitk.GetArrayFromImage(img)

    # Isolate brain region
    brainMask = binary_dilation(np.isclose(maskArr, brainnum).astype(int), iterations=4)
    brain = np.multiply(imgArr, brainMask)
    brainLoc = np.where(brainMask == 1)
    maxZ = np.max(brainLoc[0]); minZ = np.min(brainLoc[0])
    maxY = np.max(brainLoc[1]); minY = np.min(brainLoc[1])
    maxX = np.max(brainLoc[2]); minX = np.min(brainLoc[2])
    brainSmll = brain[minZ-5:maxZ+5, minY-5:maxY+5, minX-5:maxX+5]

    # Crop brain from full image
    origin = np.array(img.GetOrigin())
    spacing = np.array(img.GetSpacing())
    direction = np.array(img.GetDirection()).reshape(3, 3)

    offset = np.array([minX-5, minY-5, minZ-5])
    img_space_origin = origin + direction @ (offset * spacing)

    imgCrop = sitk.GetImageFromArray(brainSmll.astype(np.float32))
    imgCrop.SetSpacing(tuple(spacing))
    imgCrop.SetDirection(tuple(direction.flatten()))
    imgCrop.SetOrigin(tuple(img_space_origin))

    # Resample to MNI origin
    mnitemp = sitk.ReadImage(eng.getMNIpath())
    brainMNI = corrOriginToMNI(imgCrop, mnitemp)
    regDir = os.path.join(outputPath, 'registered')
    os.makedirs(regDir, exist_ok=True)
    brainPath = os.path.join(regDir,f"{filename}.nii")
    sitk.WriteImage(brainMNI, brainPath)

    # Reslice to target space
    if toSpace == 'image':
        if other is not None:
            others = {othr for othr in other}
            if inter is not None: resliced = eng.SPMregister(brainPath, others, np.array(inter))
            else: resliced = eng.SPMregister(brainPath, others)
        else: resliced = eng.SPMregister(brainPath)
        os.remove(brainPath)

        for reslice in resliced:
            rslceImg = sitk.ReadImage(reslice)
            imgReorigin = sitk.GetImageFromArray(sitk.GetArrayFromImage(rslceImg).astype(np.float32))
            imgReorigin.SetSpacing(rslceImg.GetSpacing())
            imgReorigin.SetDirection(rslceImg.GetDirection())
            imgReorigin.SetOrigin(tuple(img_space_origin))
            sitk.WriteImage(imgReorigin, reslice)
            
    # Reslice to MNI space
    elif toSpace == 'mni':
        if inter is not None:
            resliced = eng.Brainregister(brainPath, norm, np.array(inter))
        else:
            resliced = eng.Brainregister(brainPath, norm)

    if verbose:
        if toSpace == 'mni':
            print(f"Resliced brain image saved in MNI space at: \n" + resliced)
        elif toSpace == 'image':
            print(f"Resliced field maps and atlases saved in image space at: \n" + '\n'.join(resliced))
    return resliced



def imgLoad(path: str) -> sitk.Image:
    """
    Load an image from a given path using SimpleITK.
    
    Automatically handles:
    - NIfTI (.nii, .nii.gz)
    - MetaImage (.mha, .mhd)
    - NRRD (.nrrd)
    - Analyze (.hdr/.img)
    - DICOM directories or files (.dcm)

    Parameters:
        path (str): Path to the image file or DICOM directory.

    Returns:
        sitk.Image: The loaded SimpleITK image.

    Raises:
        FileNotFoundError: If the path does not exist.
        RuntimeError: If the format is not supported or load fails.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    if os.path.isdir(path):
        # Assume DICOM series
        reader = sitk.ImageSeriesReader()
        series_ids = reader.GetGDCMSeriesIDs(path)
        if not series_ids:
            raise RuntimeError(f"No DICOM series found in directory: {path}")
        series_file_names = reader.GetGDCMSeriesFileNames(path, series_ids[0])
        reader.SetFileNames(series_file_names)
        image = reader.Execute()
    else:
        # Assume single file
        image = sitk.ReadImage(path)

    return image



def corrOriginToMNI(cropped_img: sitk.Image, mni_img: sitk.Image) -> sitk.Image:
    # Extract components
    img_size = np.array(cropped_img.GetSize())
    img_spacing = np.array(cropped_img.GetSpacing())
    img_dir = np.array(cropped_img.GetDirection()).reshape(3, 3)

    mni_origin = np.array(mni_img.GetOrigin())
    mni_dir = np.array(mni_img.GetDirection()).reshape(3, 3)

    centre_voxel = img_size / 2.0
    mni_centre_physical = mni_origin + mni_dir @ (centre_voxel * img_spacing)

    corrected_origin = mni_centre_physical - img_dir @ (centre_voxel * img_spacing)

    out_img = sitk.Image(cropped_img)
    out_img.SetOrigin(tuple(corrected_origin))

    return out_img




def validate_inputs(imgPath, maskPath, toSpace, norm, outputPath=None, filename=None, other=None, inter=None):
    # Check toSpace argment
    # toSpace must be either 'Image' or 'MNI'
    tospacefin = toSpace.lower()
    if tospacefin not in ['image', 'mni']:
        raise ValueError(f"'toSpace' must be either 'Image' or 'MNI'. Got: {toSpace}") 

    # Check paths exist
    if not os.path.exists(imgPath):
        raise FileNotFoundError(f"Image path does not exist: {imgPath}")
    if not os.path.exists(maskPath):
        raise FileNotFoundError(f"Mask path does not exist: {maskPath}")
    
    # Check output path
    if outputPath is not None:
        if not os.path.exists(outputPath):
            try:
                os.makedirs(outputPath)
            except Exception as e:
                raise RuntimeError(f"Failed to create output directory '{outputPath}': {e}")
    
    # Check filename is string if provided
    if filename is not None and not isinstance(filename, str):
        raise TypeError(f"'filename' must be a string. Got: {type(filename)}")
    # Assert filename does not have a file postfix
    if filename is not None:
        if any(filename.lower().endswith(ext) for ext in ['.nii', '.nii.gz', '.img', '.hdr', '.mha', '.mhd', '.nrrd', '.dcm']):
            raise ValueError(f"'filename' should not include a file extension. Got: {filename}")
    
    # Check 'other' input
    if other is not None:
        if not isinstance(other, (list, tuple, set)):
            raise TypeError("'other' must be a list, tuple, or set of file paths.")
        for p in other:
            if not isinstance(p, str):
                raise ValueError(f"All items in 'other' must be strings. Found: {type(p)}")
            if not os.path.exists(p):
                raise FileNotFoundError(f"File in 'other' does not exist: {p}")
        if tospacefin=='mni':
            print(f"Warning: 'other' is ignored when 'toSpace' is 'MNI'. autoSPM assumes all atlases in 'other' are in MNI space.")
    
    # Validate 'inter'
    if inter is not None:
        try:
            inter_arr = list(inter)  # force list-like behaviour
        except Exception as e:
            raise ValueError(f"'inter' must be an iterable of interpolation values. Error: {e}")

        # Coerce each element to float to ensure numeric type
        try:
            inter_arr = [float(i) if not isinstance(i, (list, tuple)) else list(map(float, i)) for i in inter_arr]
        except Exception as e:
            raise ValueError(f"Each item in 'inter' must be numeric or list/tuple of numerics. Error: {e}")
    else:
        inter_arr = None

    # Check length correspondence
    if other is not None and inter_arr is not None:
        if len(other) != len(inter_arr):
            raise ValueError(f"'other' and 'inter' must be of the same length. Got: {len(other)} and {len(inter_arr)}. Please choose interpolation method(s) for each image in 'other'.")
        
    if  norm and tospacefin != 'mni':
        print(f"WARNING! Don't try to ice-skate uphill! Normalization currently only possible for registration to MNI space") 
        
def validate_brainnum(maskPath, brainnum):
    if not isinstance(brainnum, int) or brainnum < 0:
        raise ValueError(f"'brainnum' must be a non-negative integer. Got: {brainnum}")
    
    # Try loading images
    try:
        mask = imgLoad(maskPath)
    except Exception as e:
        raise RuntimeError(f"Failed to load mask image: {e}")
    
    mask_arr = sitk.GetArrayFromImage(mask)
    if not np.any(mask_arr == brainnum):
        raise ValueError(f"No voxels with label '{brainnum}' found in the mask.")

