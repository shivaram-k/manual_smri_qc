import os
import nibabel as nib
import numpy as np
from skimage.filters import threshold_otsu

def crop_brain_mri(nifti_path, output_path):
    # Load NIfTI image
    img = nib.load(nifti_path)
    img_data = img.get_fdata()

    # Apply threshold to remove background (e.g., intensity = 0)
    # Automatic thresholding
    threshold = threshold_otsu(img_data)
    mask = img_data > threshold
    
    # Check if mask is created properly
    if not np.any(mask):
        print(f"No non-zero voxels found in {nifti_path}, consider adjusting the threshold.")
        return
    
    # Get the indices where the mask is True (non-zero)
    coords = np.array(np.nonzero(mask))

    # Find the bounding box
    min_coords = coords.min(axis=1)
    max_coords = coords.max(axis=1)

    # Crop the image to the bounding box
    cropped_img_data = img_data[min_coords[0]:max_coords[0]+1,
                                min_coords[1]:max_coords[1]+1,
                                min_coords[2]:max_coords[2]+1]

    # Create a new NIfTI image from the cropped data
    cropped_img = nib.Nifti1Image(cropped_img_data, img.affine)

    # Save the cropped image
    nib.save(cropped_img, output_path)
    print(f"Cropped NIfTI image saved to {output_path}")


if __name__ == "__main__":
    import sys
    # Get input and output directories from command-line arguments
    input_scan = sys.argv[1]
    output_scan = sys.argv[2]

    # Process all NIfTI files in the directory
    crop_brain_mri(input_scan, output_scan)

