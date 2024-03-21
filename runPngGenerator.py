import subprocess as sb
import os
import glob
import nibabel
import numpy as np
import random
import pandas as pd
import sys
import argparse
import nibabel as nib

def selectSliceIndices(brainMin, brainMax):
    randRange = int(round((brainMax - brainMin)*0.05))
    # Get the slices for each dimension
    slice1 = int((brainMax - brainMin)/4 + brainMin + random.randint(-randRange, randRange))
    slice2 = int((brainMax - brainMin)/2 + brainMin + random.randint(-randRange, randRange))
    slice3 = int((brainMax - brainMin)*3/4 + brainMin + random.randint(-randRange, randRange))
    
    return [slice1, slice2, slice3]


def checkSliceHasTissue(brainSlice):
    # Make sure at least 10% of the brainSlice is actually brain
    totalPixels = len(brainSlice)*len(brainSlice[0])
    nonzeroPixels = np.count_nonzero(brainSlice)
    
    if (nonzeroPixels >= 0.1*totalPixels):
        return True
    else:
        return False


def selectBrainSlices(fn):
    # Load the masked brain image
    nibImg = nibabel.load(fn)
    img = nibImg.get_fdata()

    # # What volumes do we want?
    # # Third dim: 0 is back of head? max is front of head? AP view
    # # Second dim: coronal, 0 is top and max is bottom of skull
    # # First dim: sagittal? LR

    # Goal: identify volume of brain that's non-zero
    # Get the upper and lower bounds of brain in each dimension
    # This order of coordinates works with LAS+ orientation
    dim0Lims = np.where(img.any(axis=(1, 2)))[0]
    dim1Lims = np.where(img.any(axis=(0, 2)))[0]
    dim2Lims = np.where(img.any(axis=(0, 1)))[0]
    # LIES - This order of coordinates works with PSR+ orientations  
#    dim1Lims = np.where(img.any(axis=(1, 2)))[0]
#    dim2Lims = np.where(img.any(axis=(0, 2)))[0]
#    dim0Lims = np.where(img.any(axis=(0, 1)))[0]


    # Get the min and max of each dimension
    dim0MinBrain = sorted(set(dim0Lims))[0]
    dim0MaxBrain = sorted(set(dim0Lims))[-1]
    dim0MidBrain = (dim0MinBrain + dim0MaxBrain) // 2
    
    dim1MinBrain = sorted(set(dim1Lims))[0]
    dim1MaxBrain = sorted(set(dim1Lims))[-1]
    dim1MidBrain = (dim1MinBrain + dim1MaxBrain) // 2
    
    dim2MinBrain = sorted(set(dim2Lims))[0]
    dim2MaxBrain = sorted(set(dim2Lims))[-1]
    dim2MidBrain = (dim2MinBrain + dim2MaxBrain) // 2

    # Dimension 0
    dim0Slices = selectSliceIndices(dim0MinBrain, dim0MaxBrain)
    k = 1
    while not all([checkSliceHasTissue(img[i, :, :]) for i in dim0Slices]):
        print("Regenerating dim0 slices")
        if k % 5 == 0:
            dim0MinBrain += 1
            dim0MaxBrain -= 1
        k += 1
        dim0Slices = selectSliceIndices(dim0MinBrain, dim0MaxBrain)
    
    # Dimension 1
    dim1Slices = selectSliceIndices(dim1MinBrain, dim1MaxBrain)
    k = 1
    while not all([checkSliceHasTissue(img[:, i, :]) for i in dim1Slices]):
        print("Regenerating dim1 slices")
        if k % 5 == 0:
            dim1MinBrain += 1
            dim1MaxBrain -= 1
        k += 1
        dim1Slices = selectSliceIndices(dim1MinBrain, dim1MaxBrain)
    #dim1MidBrain = (dim1MinBrain + dim1MaxBrain) // 2
    
    # Dimension 2
    dim2Slices = selectSliceIndices(dim2MinBrain, dim2MaxBrain)
    k = 1
    while not all([checkSliceHasTissue(img[:, :, i]) for i in dim2Slices]):
        print("Regenerating dim2 slices")
        if k % 5 == 0:
            dim2MinBrain += 1
            dim2MaxBrain -= 1
        k += 1
        dim2Slices = selectSliceIndices(dim2MinBrain, dim2MaxBrain)
    #dim2MidBrain = (dim2MinBrain + dim2MaxBrain) // 2
    
    return [dim0Slices, dim1Slices, dim2Slices], [dim0MidBrain, dim1MidBrain, dim2MidBrain]


def generatePngsSingleScan(mprFn, subject, outputDir):
    freeview_command = 'freeview -cmd {cmd} '
    cmd_txt = """ -v {anatomy}:grayscale=10,500  """
 
#    # This order of coordinates works with LAS+ orientations
#    dim0_slice = ' -slice {xpos} {ymid} {zmid} \n -ss {opfn} \n  '  
#    dim1_slice = ' -slice {xmid} {ypos} {zmid} \n -ss {opfn} \n  '  
#    dim2_slice = ' -slice {xmid} {ymid} {zpos} \n -ss {opfn} \n  '  

    # This order of coordinates works with PRS+ orientations
    dim0_slice = ' -slice {ymid} {zmid} {xpos} \n -ss {opfn} \n  '  
    dim1_slice = ' -slice {ypos} {zmid} {xmid} \n -ss {opfn} \n  '  
    dim2_slice = ' -slice {ymid} {zpos} {xmid} \n -ss {opfn} \n  '  



    # Set up variables 
#    mprFn = os.path.join(FS_folder, 'mri', 'norm.mgz')          # Want to use the images without the face
    target_directory = outputDir
    os.makedirs(target_directory, exist_ok=True)
    cmd_file_x = os.path.join(target_directory, 'cmd_x.txt')
    cmd_file_y = os.path.join(target_directory, 'cmd_y.txt')
    cmd_file_z = os.path.join(target_directory, 'cmd_z.txt')

    # Start writing the command string
    sj_cmd = cmd_txt.format(
        anatomy=mprFn,
        subject=subject
    )

    brainSlices, brainMids = selectBrainSlices(mprFn)
    
    sj_cmd_x = sj_cmd + " -viewport x "
    sj_cmd_y = sj_cmd + " -viewport y "
    sj_cmd_z = sj_cmd + " -viewport z "


    for dim0Slice in brainSlices[0]:
        sj_cmd_x += dim0_slice.format(
            xpos=dim0Slice,
            ymid = brainMids[1],
            zmid = brainMids[2],
            opfn=os.path.join(target_directory, subject+"_dim0_"+str(
                dim0Slice).zfill(3) + '.png')
        ) 

    for dim1Slice in brainSlices[1]:
        sj_cmd_y += dim1_slice.format(
            xmid = brainMids[0],
            ypos=dim1Slice,
            zmid = brainMids[2],
            opfn=os.path.join(target_directory, subject+"_dim1_"+str(
                dim1Slice).zfill(3) + '.png')
        ) 

    for dim2Slice in brainSlices[2]:
        sj_cmd_z += dim2_slice.format(
            xmid = brainMids[0],
            ymid = brainMids[1],
            zpos=dim2Slice,
            opfn=os.path.join(target_directory, subject+"_dim2_"+str(
                dim2Slice).zfill(3) + '.png') 
        ) 

    with open(cmd_file_x, 'w') as f:
        sj_cmd_x += ' -quit \n '
        f.write(sj_cmd_x)
        
    with open(cmd_file_y, 'w') as f:
        sj_cmd_y += ' -quit \n '
        f.write(sj_cmd_y)
        
    with open(cmd_file_z, 'w') as f:
        sj_cmd_z += ' -quit \n '
        f.write(sj_cmd_z)

    os.system("module load FreeSurfer/7.1.1")
    sb.call(freeview_command.format(cmd=cmd_file_x), shell=True)
    sb.call(freeview_command.format(cmd=cmd_file_y), shell=True)
    sb.call(freeview_command.format(cmd=cmd_file_z), shell=True)
    
    print("PNGs generated for", subject)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-dir', help='Path to and including input BIDS directory')
    parser.add_argument('-o', '--output-dir', help='Path to output directory for QC PNG storage')
  
    args = parser.parse_args()
    inDir = args.input_dir
    
    # Load freesurfer
    # module("load", "FreeSurfer/7.1.1")  #----> Does not work!
    
    # --- Output directory --- 
    # outBase = "/home/gudapatis/SLIP_QC/pngOutputs"
    outBase = args.output_dir
    if not os.path.exists(outBase):
        os.makedirs(outBase)
        
    # --- Read participants.tsv ---
    demoPath = os.path.join(inDir, "participants.tsv")
    
    # Exit if participants.tsv not present
    if not os.path.exists(demoPath):
        print("Not a valid BIDS directory. Missing participants.tsv")
        sys.exit(1)

    demoDf = pd.read_csv(demoPath, sep="\t")
    
    # --- Get a list of subject IDs ---
    subIDs = [sub for sub in os.listdir(inDir) if "sub-" in sub]
    
    for subID in subIDs:
        # Full path to subject directory
        subPath = os.path.join(inDir, subID)
        # List of sessions
        sesIDs = [ses for ses in os.listdir(subPath) if "ses-" in ses]
        
        for sesID in sesIDs:
           sesPath = os.path.join(subPath, sesID)
           anatPath = os.path.join(sesPath, "anat")
           
           # Check if session has anat folder
           if not os.path.exists(anatPath):
               continue
           # Get the list of niftis in the anat folder
           scans = [scan for scan in os.listdir(anatPath) if ".nii" in scan and "MPR" in scan]
           
           for scan in scans:
               scanID = scan.split(".nii")[0]
               print(subID, sesID, scanID)
               scanPath = os.path.join(anatPath, scan)
               # Output directory
               outDir = os.path.join(outBase, scanID)
               if not os.path.exists(outDir):
                   os.makedirs(outDir)
                   
               # If there are already pngs for the scan
               existingPngs = glob.glob(outDir + "/*.png")
               if len(existingPngs) < 9:
                   print("Generating Image Slices for", scanID)
                   generatePngsSingleScan(scanPath, scanID, outDir)


if __name__ == "__main__":
    main()
