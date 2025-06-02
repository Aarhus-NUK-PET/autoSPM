# autoSPM

**autoSPM** is a Python-based pipeline for automatic brain segmentation and co-registration of brain field maps and atlases to PET/CT images using TotalSegmentator and SPM12 (via MATLAB). 


## Features

- Brain segmentation from CT using TotalSegmentator
- Rigid registration from MNI space to image space using SPM12 (MATLAB)
- Optional co-registration of additional images
- Handles any image format that can be loaded with SimpleITK

## Dependencies

- TotalSegmentator (https://github.com/wasserth/TotalSegmentator)
- SPM12 (installed and configured in MATLAB) (https://www.fil.ion.ucl.ac.uk/spm/)
- MATLAB Engine API for Python (https://se.mathworks.com/help/matlab/matlab-engine-for-python.html)

## Usage

```bash
python run_autoSPM.py \
    --toSegment <path_to_image_for_spm> \
    --ctPath <path_to_corresponding_ct> \
    --outputDir <directory_to_save_imgs_to> \
```

This outputs:
```graphql
outputDir/
├── registered/        
│   ├── avg152T1.nii          # The average T1 image from SPM
│   ├── csf.nii               # CSF probabilit map
│   ├── grey.nii              # Grey matter probabilit map
│   └── white.nii             # White matter probabilit map
├── brain.nii.gz              # Brain segmentation from TotalSegmentator
```

Other settings:
* `--other`: Other images/atlases in MNI space to coregister. Takes a space separated list of paths
*      e.g. ` --other 'path/atlas1.nii' 'path/atlas2.nii'`
* `--inter`: Interpolation procedures to follow the arguments from --other. Takes a space separated list of numbers of equal size to other, e.g. 0 1 (All set to 0 (nearest neighbour) if not provided)
*      e.g. ` --inter 0 1`

## Note!
This code is intended for academic and research use only. Please cite the appropriate references when using TotalSegmentator or SPM in publications.
