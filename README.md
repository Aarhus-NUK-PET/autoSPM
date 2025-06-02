# autoSPM
autoSPM is a package that performs an automatic registration of SPM field maps to total-body PET/CT images in the PET space.

Dependencies:
- TotalSegmentator (and Pytorch)
- MATLAB Python engine (https://se.mathworks.com/help/matlab/matlab-engine-for-python.html)
- SimpleITK, scipy, numpy, etc

Install autoSPM:
```
git clone ...
cd autoSPM
```

Run:
```
python run_autoSPM.py --toSegment <path_to_image_for_spm> --ctPath <path_to_corresponding_ct> --ouputDir <directory_to_save_imgs_to>
```
