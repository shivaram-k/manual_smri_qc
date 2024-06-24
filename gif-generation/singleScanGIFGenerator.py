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
from nilearn import plotting, datasets, image
from nilearn.image import coord_transform
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import imageio
import matplotlib.colors as mcolors

##
# Select slices with step_size of 3  from the 25th to 75th percentile indices from one dimension of the brain
# @parameter brainMin The lower bound of the brain in that dimension
# @parameter brainMax The upper bound of the brain in that dimension
# @return brainSliceIndices A list of selected slice indices
def selectSliceIndices(brainMin, brainMax):

    step_size = 3
    slices = []
    # Calculate the range
    range_values = brainMax - brainMin
    
    # Calculate the values corresponding to the 25th and 75th percentiles
    sliceBeg = brainMin + (range_values * 0.25)
    sliceEnd = brainMin + (range_values * 0.75)
    
    # Convert values to indices
    sliceBeg = int(sliceBeg)
    sliceEnd = int(sliceEnd)
    
    for s in range(sliceBeg, sliceEnd+step_size, step_size):
        slices.append(s)
    
    return slices


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
    
def map_ss_labels(segImg, segData):
	
    value_mapping = {
    0.0 : 0.0,
    2.0 : 2.0, 41.0 : 2.0,
    3.0 : 3.0, 42.0 : 3.0,
    4.0 : 4.0, 5.0 : 4.0, 14.0 : 4.0, 15.0 : 4.0, 24.0 : 4.0, 43.0 : 4.0, 44.0 : 4.0, 
    7.0 : 7.0, 46.0 : 7.0,
    8.0 : 8.0, 47.0 : 8.0,
    10.0 : 10.0, 11.0 : 10.0, 12.0 : 10.0, 13.0 : 10.0, 17.0 : 10.0, 18.0 : 10.0,
    49.0 : 10.0, 50.0 : 10.0, 51.0 : 10.0, 52.0 : 10.0, 53.0 : 10.0, 54.0 : 10.0,
    26.0 : 10.0, 28.0 : 10.0, 58.0 : 10.0, 60.0 : 10.0,
    16.0 : 16.0,    
    }
	
    # Custom function to handle mapping and default value
    def map_and_default(value):
        return value_mapping.get(value, default_value)
	
    # Define a default value if a key is not found in the mapping
    default_value = round(np.max(segData)/100,0)
	
    # Apply mapping and default value using NumPy vectorized operation
    mappedData = np.vectorize(map_and_default)(segData)
	
    # Save the modified image
    modified_segImg = nibabel.Nifti1Image(mappedData, segImg.affine)
	
    return mappedData, modified_segImg

def get_cmap(mappedData):

    all_colors = [
    "#ffff00", #yellow
    "#0036ff", #blue
    "#ff00c5", #magenta
    "#0fff1e", #green
     "cyan",
     '#9600f8', #purple
     "#ff8f00", #orange
     "red"
     ]
     
    # Define a custom colormap with unique colors for each label
    num_labels = len(np.unique(mappedData))
    colors = all_colors[:num_labels]
    cmap = mcolors.ListedColormap(colors)
    
    return cmap
    
## 
# Use the nibabel library to generate a set of PNGs from a brain scan
# @parameter scanFn A string representing the full path to a scan
# @parameter subject A string of the subject's identifier
# @parameter outputDir A string specifying the directory to save the PNGs to
# @return None
def generateGIFsSingleScanNibabel(scanPath, segPath, scanID, outBase):


    # Load the masked brain image
    nibImg = nibabel.load(scanPath)
    img = nibImg.get_fdata()
    aff = nibImg.affine
    
    # Load the segmentation
    segImg = nibabel.load(segPath)
    segData = segImg.get_fdata()
    
    # Map labels to make it easier for custom color map
    mappedData, modified_segImg = map_ss_labels(segImg, segData)
    
    # Get custom color map
    cmap = get_cmap(mappedData)
    
    # Select slices to make GIFs
    brainSlices = selectNewSliceCoordinates(img)
    
    # ---------- Dim0 ----------
    # Create a directory to temporarily store PNGs that will be used to create the GIF
    outImages_y = os.path.join(outBase, "images_y")
    if not os.path.exists(outImages_y):
    	os.makedirs(outImages_y)
    	
    # List of image files for each slice along Dim0
    images_y = []
    
    # Dim0 in pixel space corresponds to coronal view (dim1) in MNI space
    for dim0Slice in brainSlices[0]:
        newSlice = coord_transform(dim0Slice, 0, 0, aff)
        newFn = os.path.join(outImages_y, f'slice_{newSlice[1]}_y.png')
        fig = plt.figure(figsize=(6, 6))
        plotting.plot_roi(roi_img=modified_segImg, bg_img=nibImg,display_mode="y", cut_coords=[newSlice[1]], draw_cross=False,\
                     dim = -0.7, alpha = 0.4, cmap=cmap, figure = fig, annotate=False)
        
        plt.axis('off')
    
        # Save current frame as image
        plt.savefig(newFn, bbox_inches='tight')

        # Append image to list of frames
        images_y.append(newFn)
        plt.close('all')  # Close all figures after saving
        
    # Create GIF
    outGIF_y = os.path.join(outBase, scanID+"_dim0.gif")
    imageio.mimsave(outGIF_y, [imageio.imread(img) for img in images_y], fps=3)
    
    # Check if the GIF file was created successfully
    if os.path.exists(outGIF_y):
        # Remove the PNG files if the GIF was created successfully
        rm_cmd = "rm -rf " + outImages_y
        os.system(rm_cmd)
    else:
        print("Failed to create Dim0 GIF file for ", scanID, ". PNG files are not removed.")
    
    # ---------- ---- ----------
    
    # ---------- Dim1 ----------
    # Create a directory to temporarily store PNGs that will be used to create the GIF
    outImages_z = os.path.join(outBase, "images_z")
    if not os.path.exists(outImages_z):
    	os.makedirs(outImages_z)
    	
    # List of image files for each slice along Dim0
    images_z = []
 
    # Dim1 in pixel space corresponds to dim2 in MNI space
    for dim1Slice in brainSlices[1]:
        newSlice = coord_transform(0, dim1Slice, 0, aff)
        newFn = os.path.join(outImages_z, f'slice_{newSlice[2]}_z.png')
        fig = plt.figure(figsize=(6, 6))
        plotting.plot_roi(roi_img=modified_segImg, bg_img=nibImg,display_mode="z", cut_coords=[newSlice[2]], draw_cross=False,\
                     dim = -0.7, alpha = 0.4, cmap=cmap, figure = fig, annotate=False)
        
        plt.axis('off')
    
        # Save current frame as image
        plt.savefig(newFn, bbox_inches='tight')

        # Append image to list of frames
        images_z.append(newFn)
        plt.close('all')  # Close all figures after saving
        
    # Create GIF
    outGIF_z = os.path.join(outBase, scanID+"_dim1.gif")
    imageio.mimsave(outGIF_z, [imageio.imread(img) for img in images_z], fps=3)
    
    # Check if the GIF file was created successfully
    if os.path.exists(outGIF_z):
        # Remove the PNG files if the GIF was created successfully
        rm_cmd = "rm -rf " + outImages_z
        os.system(rm_cmd)
    else:
        print("Failed to create Dim1 GIF file for ", scanID, ". PNG files are not removed.")
    
    # ---------- ---- ----------
    
    # ---------- Dim2 ----------
    # Create a directory to temporarily store PNGs that will be used to create the GIF
    outImages_x = os.path.join(outBase, "images_x")
    if not os.path.exists(outImages_x):
    	os.makedirs(outImages_x)
    	
    # List of image files for each slice along Dim0
    images_x = []

    # Dim2 in pixel space corresponds to dim0 in MNI space
    for dim2Slice in brainSlices[2]:
        newSlice = coord_transform(0, 0, dim2Slice, aff)
        newFn = os.path.join(outImages_x, f'slice_{newSlice[0]}_x.png')
        fig = plt.figure(figsize=(6, 6))
        plotting.plot_roi(roi_img=modified_segImg, bg_img=nibImg,display_mode="x", cut_coords=[newSlice[0]], draw_cross=False,\
                     dim = -0.7, alpha = 0.4, cmap=cmap, figure = fig, annotate=False)
                     
        plt.axis('off')
        
        # Save current frame as image
        plt.savefig(newFn, bbox_inches='tight')

        # Append image to list of frames
        images_x.append(newFn)
        plt.close('all')  # Close all figures after saving
        
    # Create GIF
    outGIF_x = os.path.join(outBase, scanID+"_dim2.gif")
    imageio.mimsave(outGIF_x, [imageio.imread(img) for img in images_x], fps=3)
    
    # Check if the GIF file was created successfully
    if os.path.exists(outGIF_x):
        # Remove the PNG files if the GIF was created successfully
        rm_cmd = "rm -rf " + outImages_x
        os.system(rm_cmd)
    else:
        print("Failed to create Dim2 GIF file for ", scanID, ". PNG files are not removed.")
    
    # ---------- ---- ----------

    print("GIFs generated for", scanID)

##
# Main function
def main():
    # --- Set up the argument parser ---
    parser = argparse.ArgumentParser()
    # Add an argument to get the scan to generate PNGs from --> Required!
    parser.add_argument('-f', '--scan-fn', help='Full path to the .nii(.gz) scan', required = True)
    # Add an argument to get the directory where the QC PNGs will be written --> Required!
    parser.add_argument('-o', '--out-dir', help='Full path to the directory where the PNG files should be written to', required = True)
    # Add an optional argument to get the derivatives directory for synthseg overlay PNGs --> Optional!
    parser.add_argument('-d', '--der-fn', help='Full path to the synthseg segmentation nifti ')

    args = parser.parse_args()
    scanPath = args.scan_fn
    outBase = args.out_dir
    segPath = args.der_fn

    scanID = scanPath.split("/")[-1].split(".nii")[0]
    # Make the output directory if it doesn't exist
    outDir = os.path.join(outBase, scanID)
    if not os.path.exists(outDir):
        os.makedirs(outDir)
                   
    generateGIFsSingleScanNibabel(scanPath, segPath, scanID, outDir)


if __name__ == "__main__":
    main()
    print("The script has finished running")
