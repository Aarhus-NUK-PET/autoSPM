# autoSPM

**autoSPM** is a Python-based pipeline for automatic brain segmentation and co-registration of PET/CT images using TotalSegmentator and SPM12 (via MATLAB).

---

## Features

- Brain segmentation from CT using TotalSegmentator
- Rigid registration to MNI space via SPM12 (MATLAB)
- Optional co-registration of additional images
- Handles any image format that can be loaded with SimpleITK

---

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
├── brain.nii.gz              # Brain segmentatio from TotalSegmentator
```

Other settings:
* `--other`: Other images/atlases in MNI space to coregister. Takes a list of paths, e.g. ['path/atlas1.nii', 'path/atlas2.nii']
* `--inter`: Interpolation procedures to follow the arguments from --other. Takes a list of numbers of equal size to other, e.g. [0, 1]
