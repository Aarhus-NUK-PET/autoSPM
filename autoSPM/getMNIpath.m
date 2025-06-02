function dir = getMNIpath()
    % getMNIpath - Get the directory of the MNI template used in SPM
    %
    % Syntax:
    %   dir = getMNIpath()
    %
    % Outputs:
    %   dir - The directory where SPM is installed

    spmDir = spm('Dir');
    
    if isempty(spmDir)
        error('SPM is not installed or not added to the MATLAB path.');
    end
    
    mniDir = fullfile(spmDir, 'canonical', 'avg152T1.nii');
    if ~exist(mniDir, 'file')
        error('MNI template file avg152T1.nii does not exist in the SPM canonical directory.');
    end
    dir = mniDir;
end