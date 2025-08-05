function registered = Brainregister(BrainPET, nonrigid, interpol)
    %SPMRESCLICE Summary of this function goes here
    %   Detailed explanation goes here
    if nargin < 2
        interpol = 4;
    elseif ~isempty(interpol)
        if ~isnumeric(interpol) || numel(interpol) ~= numel({BrainPET})
            error('The "interpol" argument must be a numeric vector one element".');
        end
    end
    
    mnispace = fullfile(spm('Dir'),'canonical','avg152T1.nii');

    matlabbatch{1}.spm.spatial.coreg.estimate.ref = cellstr(mnispace);
    matlabbatch{1}.spm.spatial.coreg.estimate.source = cellstr(BrainPET);
    matlabbatch{1}.spm.spatial.coreg.estimate.other = {''};
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.cost_fun = 'nmi'; % Normalized Mutual Information
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.sep = [4 2]; % Optimization steps
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.tol = [0.0200 0.0200 0.0200 0.0010 0.0010 0.0010 0.0100 0.0100 0.0100 0.0010 0.0010 0.0010]; 
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.fwhm = [4 4]; % Gaussian smoothing

    spm_jobman('run', matlabbatch);

    if nonrigid
        matlabbatch{1}.spm.spatial.normalise.estwrite.subj.vol = cellstr(BrainPET);
        matlabbatch{1}.spm.spatial.normalise.estwrite.subj.resample = cellstr(BrainPET);
        matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.biasreg = 0.0001;
        matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.biasfwhm = 60;
        matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.tpm = {fullfile(spm('Dir'),'tpm','TPM.nii')};
        matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.affreg = 'mni';
        matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.reg = [0 0.001 0.5 0.05 0.2];
        matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.fwhm = 0;
        matlabbatch{1}.spm.spatial.normalise.estwrite.eoptions.samp = 3;
        matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.bb = [-78 -112 -70; 78 76 85];
        matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.vox = [2 2 2];
        matlabbatch{1}.spm.spatial.normalise.estwrite.woptions.interp = 4;
        spm_jobman('run', matlabbatch);
    else
        P = char(mnispace, BrainPET);  % Reference first
        spm_reslice(P, struct('interp', double(interpol(1)), 'mask', 0, 'which', 1, 'mean', 0, 'prefix', ''));
    end
    
    
    registered = BrainPET;
end