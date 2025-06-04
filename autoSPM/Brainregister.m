function registered = Brainregister(BrainPET, interpol)
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

    P = char(mnispace, BrainPET);  % Reference first
    spm_reslice(P, struct('interp', double(interpol(1)), 'mask', 0, 'which', 1, 'mean', 0, 'prefix', ''));
    
    registered = BrainPET;
end