import subprocess as sb
import os
import glob
import nibabel
import numpy as np
import random
import pandas as pd

def selectSliceIndices(brainMin, brainMax):
    # Get the slices for each dimension
    slice1 = int((brainMax - brainMin)/4 + brainMin + random.randint(-12, 12))
    slice2 = int((brainMax - brainMin)/2 + brainMin + random.randint(-12, 12))
    slice3 = int((brainMax - brainMin)*3/4 + brainMin + random.randint(-12, 12))

    return [slice1, slice2, slice3]

def selectBrainSlices(folder):
    # Load the masked brain image
    nibImg = nibabel.load(FS_folder+"mri/norm.mgz")
    img = nibImg.get_fdata()

    # # What volumes do we want?
    # # Third dim: 0 is back of head? max is front of head? AP view
    # # Second dim: coronal, 0 is top and max is bottom of skull
    # # First dim: sagittal? LR

    # Goal: identify volume of brain that's non-zero
    # Get the upper and lower bounds of brain in each dimension
    dim0Lims, dim1Lims = np.where(img.any(axis=2))
    _, dim2Lims = np.where(img.any(axis=1))

    # Get the min and max of each dimension
    dim0MinBrain = sorted(set(dim0Lims))[0]
    dim0MaxBrain = sorted(set(dim0Lims))[-1]
    dim1MinBrain = sorted(set(dim1Lims))[0]
    dim1MaxBrain = sorted(set(dim1Lims))[-1]
    dim2MinBrain = sorted(set(dim2Lims))[0]
    dim2MaxBrain = sorted(set(dim2Lims))[-1]

    dim0Slices = selectSliceIndices(dim0MinBrain, dim0MaxBrain)
    dim1Slices = selectSliceIndices(dim1MinBrain, dim1MaxBrain)
    dim2Slices = selectSliceIndices(dim2MinBrain, dim2MaxBrain)


    return [dim0Slices, dim1Slices, dim2Slices]

def generatePngsSingleScan(FS_folder, subject, outputDir):
    freeview_command = 'freeview -cmd {cmd} '
    cmd_txt = """ -v {anatomy}:grayscale=10,100 -f {lh_wm}:color=blue:edgecolor=blue -f {rh_wm}:color=blue:edgecolor=blue -f {lh_pial}:color=red:edgecolor=red -f {rh_pial}:color=red:edgecolor=red
     -viewport sagittal
     """  

    # To step through the sagittal slices this is added for every slice. 
    dim0_slice = ' -slice {xpos} 127 127 \n -ss {opfn} \n  '  
    dim1_slice = ' -slice 127 {xpos} 127 \n -ss {opfn} \n  '  
    dim2_slice = ' -slice 127 127 {xpos} \n -ss {opfn} \n  '  

    # Set up variables 
    mprFn = os.path.join(FS_folder, 'mri', 'norm.mgz')          # Want to use the images without the face
#     target_directory = os.path.join(FS_folder, 'pngs')          # Directory to save the pngs to
    target_directory = outputDir
    os.makedirs(target_directory, exist_ok=True)
    cmd_file = os.path.join(target_directory, 'cmd.txt')

    # Start writing the command string
    sj_cmd = cmd_txt.format(
        anatomy=mprFn,
        lh_wm=os.path.join(FS_folder, 'surf', 'lh.white'),
        lh_pial=os.path.join(FS_folder, 'surf', 'lh.pial'),
        rh_wm=os.path.join(FS_folder, 'surf', 'rh.white'),
        rh_pial=os.path.join(FS_folder, 'surf', 'rh.pial'),
        subject=subject
    )

    brainSlices = selectBrainSlices(mprFn)

    for dim0Slice in brainSlices[0]:
        sj_cmd += dim0_slice.format(
            xpos=dim0Slice,
            opfn=os.path.join(target_directory, subject+"_dim0_"+str(
                dim0Slice).zfill(3) + '.png')
        )

    for dim1Slice in brainSlices[1]:
        sj_cmd += dim1_slice.format(
            xpos=dim1Slice,
            opfn=os.path.join(target_directory, subject+"_dim1_"+str(
                dim1Slice).zfill(3) + '.png')
        )

    for dim2Slice in brainSlices[2]:
        sj_cmd += dim2_slice.format(
            xpos=dim2Slice,
            opfn=os.path.join(target_directory, subject+"_dim2_"+str(
                dim2Slice).zfill(3) + '.png') 
        )

    # Add the end of the command
    sj_cmd += ' -quit \n '

    with open(cmd_file, 'w') as f:
        f.write(sj_cmd)

    sb.call(freeview_command.format(cmd=cmd_file), shell=True)
    
    print("PNGs generated for", subject)


def main():
    subjDir = "/Users/youngjm/Data/clip/images/derivatives/mpr_fs_reconall_6.0.0/"
    fn = '/Users/youngjm/Data/clip/tables/CLIPv0.7/2022-05-26_highres_nocontrast_singlescanpersubject.csv'
    outputDir = "/Users/youngjm/Data/clip/images/derivatives/qc_mpr_fs_6.0.0/"

    df = pd.read_csv(fn)
    
    # Get the ids of the scans we want graded
    scanIds = df['scan_id'].values
    
    # For each scan
    for scanId in scanIds:
        # Identify the complete path to the scan
        subj = scanId.split("_")[0]
        ses = scanId.split("_")[1]
    
        scanPath = subjDir+subj+"/"+ses+"/anat/"+scanId+"/"
        generatePngsSingleScan(scanPath, subj, outputDir)

if __name__ == "__main__":
    main()
