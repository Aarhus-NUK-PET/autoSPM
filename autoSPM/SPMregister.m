function registered = SPMregister(BrainPET, paths, interpol)
    %SPMRESCLICE Summary of this function goes here
    %   Detailed explanation goes here
    if nargin < 2
        paths = [];
    end
    if nargin < 3
        interpol = [];
    end
    
    otherpaths = ~isempty(paths);
    [path,~,~] = fileparts(BrainPET);
    files = copySPMfiles(path, otherpaths, paths);

    if ~isempty(interpol)
        if ~isnumeric(interpol) || numel(interpol) ~= numel(paths)
            error('The "interpol" argument must be a numeric vector with the same number of elements as "paths".');
        end
    end
    N = numel(files);
    inter = zeros(1, N);
    inter(1:min(N,4)) = 1;

    if ~isempty(interpol)
        inter(5:end) = 0;
        inter(5:end) = interpol;
    end


    matlabbatch{1}.spm.spatial.coreg.estimate.ref = cellstr(BrainPET);
    matlabbatch{1}.spm.spatial.coreg.estimate.source = files(1);
    matlabbatch{1}.spm.spatial.coreg.estimate.other = files(2:end);
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.cost_fun = 'nmi'; % Normalized Mutual Information
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.sep = [4 2]; % Optimization steps
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.tol = [0.0200 0.0200 0.0200 0.0010 0.0010 0.0010 0.0100 0.0100 0.0100 0.0010 0.0010 0.0010]; 
    matlabbatch{1}.spm.spatial.coreg.estimate.eoptions.fwhm = [4 4]; % Gaussian smoothing

    spm_jobman('run', matlabbatch);

    for i = 1:numel(files)
        P = char(BrainPET, files{i});  % Reference first
        spm_reslice(P, struct('interp', inter(i), 'mask', 0, 'which', 1, 'mean', 0, 'prefix', ''));
    end
    
    registered = files;
end


function files = copySPMfiles(path, otherpaths, paths)
    if ~exist(strcat(path, '/registered'), 'dir'), mkdir(path, 'registered') 
    end
    files = {};
    files = [files; copyFile(fullfile(spm('Dir'),'canonical','avg152T1.nii'),path)];
    files = [files; copyFile(fullfile(spm('Dir'),'toolbox', 'FieldMap', 'csf.nii'),path)];
    files = [files; copyFile(fullfile(spm('Dir'),'toolbox', 'FieldMap', 'white.nii'),path)];
    files = [files; copyFile(fullfile(spm('Dir'),'toolbox', 'FieldMap', 'grey.nii'),path)];
    if otherpaths
        for i = 1:length(paths)
            if ~exist(paths{i}, 'file'),error('The file %s does not exist.', paths{i}); end
           files = [files; copyFile(char(paths(i)), path)];
        end
    end


end


function filename = copyFile(root, newpath)
    [~,name,ext] = fileparts(root);
    if contains(name, '.nii') && strcmp(ext, '.gz')
        outdir = fullfile(newpath, 'registered');
        if ~exist(outdir, 'dir'), mkdir(outdir); end
        filenames = gunzip(root, outdir);
        filename = filenames{1};
    elseif strcmp(ext, '.nii')
        filename = fullfile(newpath, 'registered', strcat(name,ext));
        copyfile(root, filename)
    else
        error('The file %s is not a valid NIfTI file.', root);
    end

    
end