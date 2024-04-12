
import matplotlib.colors as mcolors
import nibabel
import numpy as np
from nilearn import plotting
import os
import glob

def map_ss_labels(seg_img, synthseg_data):
	
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
	default_value = round(np.max(synthseg_data)/100,0)
	
	# Apply mapping and default value using NumPy vectorized operation
	mapped_data = np.vectorize(map_and_default)(synthseg_data)
	
	# Save the modified image
	modified_seg_img = nibabel.Nifti1Image(mapped_data, seg_img.affine)
	
	return mapped_data, modified_seg_img

def plotOverlay(mapped_data, modified_seg_img, anat_img, display_mode, coords, outFn):

	all_colors = [
	(0.0, 1.0, 0.0),  # Green
	(0.0, 0.0, 1.0),  # Blue
	(1.0, 1.0, 0.0),  # Yellow
	(1.0, 0.0, 1.0),  # Magenta
	(1.0, 0.0, 0.0),  # Red
	(1.0, 0.75, 0.0),  # Gold
	(0.0, 1.0, 1.0),  # Cyan
	(0.5, 0.0, 1.0),   # Purple
	(1.0, 0.5, 0.0),  # Orange
	]
	
	# Define a custom colormap with unique colors for each label
	num_labels = len(np.unique(mapped_data))
	colors = all_colors[:num_labels]
	cmap = mcolors.ListedColormap(colors)

	# Plot the SynthSeg segmentation map with unique colors for each label
	plotting.plot_roi(roi_img=modified_seg_img, bg_img=anat_img, cmap=cmap, draw_cross = False, dim = -0.7,\
	display_mode=display_mode, cut_coords=coords,\
	alpha = 0.4, colorbar = True, output_file = outFn)
	

def generateOverlay(segPath, scanID, anat_img, display_mode, coords, outBase, newFnBase):
	
	# Change outBase to outBase_SS_Overlays
	outBase = outBase + "_SS_Overlays"
	outPath = os.path.join(outBase, scanID)
	outFn = os.path.join(outPath, newFnBase+".png")
	
	# Make the output directory
	if not os.path.exists(outPath):
		os.makedirs(outPath)
		
	# Read the ss nifti
	
	seg_img = nibabel.load(segPath)
	synthseg_data = seg_img.get_fdata()
	
	# Map labels to make it easier for custom color map
	mapped_data, modified_seg_img = map_ss_labels(seg_img, synthseg_data)
	
	# Plot the overlay
	plotOverlay(mapped_data, modified_seg_img, anat_img, display_mode, coords, outFn)
	


def main():
	# Complete this function so the file can be run separately too
	pass

