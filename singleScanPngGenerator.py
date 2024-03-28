import subprocess as sb
import os
import glob
import numpy as np
import random
import pandas as pd
import sys
import argparse
import json
import nibabel
from nilearn import plotting
from nilearn.image import coord_transform

##
# Select 3 pseudorandom slices from one dimension of the brain
# @parameter brainMin The lower bound of the brain in that dimension
# @parameter brainMax The upper bound of the brain in that dimension
# @return brainSliceIndices A list of 3 pseudorandomly selected slice indices
def selectSliceIndices(brainMin, brainMax):
    randRange = int(round((brainMax - brainMin)*0.05))
    # Get the slices for each dimension
    slice1 = int((brainMax - brainMin)/4 + brainMin + random.randint(-randRange, randRange))
    slice2 = int((brainMax - brainMin)/2 + brainMin + random.randint(-randRange, randRange))
    slice3 = int((brainMax - brainMin)*3/4 + brainMin + random.randint(-randRange, randRange))
    
    return [slice1, slice2, slice3]


##
# Check that the contents of an image slice is at least 10% tissue
# @parameter brainSlice The numpy array containing the image data for a single slice
# @return True or False based on the number of nonzero pixels in the slice
def checkSliceHasTissue(brainSlice):
    # Make sure at least 10% of the brainSlice is actually brain
    totalPixels = len(brainSlice)*len(brainSlice[0])
    nonzeroPixels = np.count_nonzero(brainSlice)
    
    if (nonzeroPixels >= 0.1*totalPixels):
        return True
    else:
        return False


##
# Pick a set of
# @parameter img A numpy array of a 3D brain image
# @return A list of 3 lists containing the selected slice indices for each of the 3 dimensions of the iamge
def selectNewSliceCoordinates(img):
    # Goal: identify volume of brain that's non-zero
    # Get the upper and lower bounds of brain in each dimension
    dim0Lims = np.where(img.any(axis=(1, 2)))[0]
    dim1Lims = np.where(img.any(axis=(0, 2)))[0]
    dim2Lims = np.where(img.any(axis=(0, 1)))[0]

    # Get the min and max of each dimension
    dim0MinBrain = sorted(set(dim0Lims))[0]
    dim0MaxBrain = sorted(set(dim0Lims))[-1]
    
    dim1MinBrain = sorted(set(dim1Lims))[0]
    dim1MaxBrain = sorted(set(dim1Lims))[-1]
    
    dim2MinBrain = sorted(set(dim2Lims))[0]
    dim2MaxBrain = sorted(set(dim2Lims))[-1]

    # Dimension 0
    dim0Slices = selectSliceIndices(dim0MinBrain, dim0MaxBrain)
    k = 1
    # If the image does not consist of at least 10% tissue, regenerate
    while not all([checkSliceHasTissue(img[i, :, :]) for i in dim0Slices]):
        print("Regenerating dim0 slices")
        # If reselecting the slices does not produce slices with >10% 
        #  tissue content after 5 reselections, reduce the space
        #  available for the slices to be selected from
        if k % 5 == 0:
            dim0MinBrain += 1
            dim0MaxBrain -= 1
        k += 1
        dim0Slices = selectSliceIndices(dim0MinBrain, dim0MaxBrain)
    
    # Dimension 1
    dim1Slices = selectSliceIndices(dim1MinBrain, dim1MaxBrain)
    k = 1
    # If the image does not consist of at least 10% tissue, regenerate
    while not all([checkSliceHasTissue(img[:, i, :]) for i in dim1Slices]):
        print("Regenerating dim1 slices")
        # If reselecting the slices does not produce slices with >10% 
        #  tissue content after 5 reselections, reduce the space
        #  available for the slices to be selected from
        if k % 5 == 0:
            dim1MinBrain += 1
            dim1MaxBrain -= 1
        k += 1
        dim1Slices = selectSliceIndices(dim1MinBrain, dim1MaxBrain)
    
    # Dimension 2
    dim2Slices = selectSliceIndices(dim2MinBrain, dim2MaxBrain)
    k = 1
    # If the image does not consist of at least 10% tissue, regenerate
    while not all([checkSliceHasTissue(img[:, :, i]) for i in dim2Slices]):
        print("Regenerating dim2 slices")
        # If reselecting the slices does not produce slices with >10% 
        #  tissue content after 5 reselections, reduce the space
        #  available for the slices to be selected from
        if k % 5 == 0:
            dim2MinBrain += 1
            dim2MaxBrain -= 1
        k += 1
        dim2Slices = selectSliceIndices(dim2MinBrain, dim2MaxBrain)
    
    return [dim0Slices, dim1Slices, dim2Slices]

## 
# Use the nibabel library to generate a set of PNGs from a brain scan
# @parameter scanFn A string representing the full path to a scan
# @parameter subject A string of the subject's identifier
# @parameter outputDir A string specifying the directory to save the PNGs to
# @return None
def generatePngsSingleScanNibabel(scanFn, subject, outputDir):
    # Load the masked brain image
    nibImg = nibabel.load(scanFn)
    img = nibImg.get_fdata()
    aff = nibImg.affine
    
    # Select the desired slices to get PNGs of
    brainSlices = selectNewSliceCoordinates(img)

    # Dim0 in pixel space corresponds to coronal view (dim1) in MNI space
    for dim0Slice in brainSlices[0]:
        newSlice = coord_transform(dim0Slice, 0, 0, aff)
        newFn = subject+"_coronal_slice"+str(int(newSlice[1])).zfill(3)+".png"
        plotting.plot_anat(nibImg, display_mode="y", cut_coords=[newSlice[1]], draw_cross = False, output_file=os.path.join(outputDir, newFn))
 
    # Dim1 in pixel space corresponds to dim2 in MNI space
    for dim1Slice in brainSlices[1]:
        newSlice = coord_transform(0, dim1Slice, 0, aff)
        newFn = subject+"_axial_slice"+str(int(newSlice[2])).zfill(3)+".png"
        plotting.plot_anat(nibImg, display_mode="z", cut_coords=[newSlice[2]], draw_cross = False, output_file=os.path.join(outputDir, newFn))

    # Dim2 in pixel space corresponds to dim0 in MNI space
    for dim2Slice in brainSlices[2]:
        newSlice = coord_transform(0, 0, dim2Slice, aff)
        newFn = subject+"_sagittal_slice"+str(int(newSlice[0])).zfill(3)+".png"
        plotting.plot_anat(nibImg, display_mode="x", cut_coords=[newSlice[0]], draw_cross = False, output_file=os.path.join(outputDir, newFn))
  

    print("PNGs generated for", subject)

##
# Main function
def main():
    # --- Set up the argument parser ---
    parser = argparse.ArgumentParser()
    # Add an argument to get the scan to generate PNGs from
    parser.add_argument('-f', '--scan-fn', help='Full path to the .nii(.gz) scan')
    # Add an argument to get the directory where the QC PNGs will be written
    parser.add_argument('-o', '--out-dir', help='Full path to the directory where the PNG files should be written to')

    args = parser.parse_args()
    scanPath = args.scan_fn
    outBase = args.out_dir

    scanID = scanPath.split("/")[-1].split(".nii")[0]
    # Make the output directory if it doesn't exist
    outDir = os.path.join(outBase, scanID)
    if not os.path.exists(outDir):
        os.makedirs(outDir)
                   
    # If there are already pngs for the scan
    existingPngs = glob.glob(outDir + "/*.png")
    if len(existingPngs) < 9: # TODO: generalize for more PNGS
        print("Generating Image Slices for", scanID)
        generatePngsSingleScanNibabel(scanPath, scanID, outDir)


if __name__ == "__main__":
    main()
    print("The script has finished running")
