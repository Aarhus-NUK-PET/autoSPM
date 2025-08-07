# autoSPM

**autoSPM** is a Python-based pipeline for automatic brain segmentation and normalization to MNI-space from total-body PET/CT images using TotalSegmentator and SPM12 (via MATLAB).  


## Features

- Brain segmentation from CT using TotalSegmentator
- Normalization of isolated brain from total-body PET/CT to MNI space  using SPM12 (MATLAB)
- Optionally handles rigid registration of field maps and atlases from MNI space to image space
- Handles any image format that can be loaded with SimpleITK (Not thoroughly tested)

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
│   ├── Brain.nii             # Co-registered brain in MNI space
│   ├── wBrain.nii            # Normalized brain
│   └── y_Brain.nii           # Deformation field encoding the displacement to MNI space
├── brain.nii.gz              # Brain segmentation from TotalSegmentator
```

Other settings:
* `--filename`: Filename of resulting registered brain. `'Brain'` is default. (Do not include file extension)
* `--nonorm`: Skips final nomalization step and thus only performs rigid co-registration to MNI space
* `--inter`: The interpolation procedure for reslicing of the brain to MNI space. `4` is default (must be an integer)
* `--toSpace`: Final image space. `--toSpace "MNI"` is default and registers isolated brain to MNI space, `--toSpace "image"` registers field maps and atlases to image space

If `--toSpace` is `"image"` then:  
  * `--other`: Other images/atlases in MNI space to coregister. Takes a space-separated list of paths
    * e.g. ` --other 'path/atlas1.nii' 'path/atlas2.nii'`
  * `--inter`: Interpolation procedures to follow the arguments from --other. Takes a space-separated list of numbers of equal size to other, e.g. 0 1 (All set to 0 (nearest neighbour) if not provided)
    * e.g. ` --inter 0 1`
  * Output structure stays the same, but the contents of the `registered` folder is now the MNI space average T1 image, field maps for grey mater, white matter and csf (plus additional atlases specified in `--other`)  

## Note!
This code is intended for academic and research use only. Please cite the appropriate references when using TotalSegmentator or SPM in publications.
