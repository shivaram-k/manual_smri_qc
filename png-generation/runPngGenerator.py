
"""
This script currently looks for anat MPR labeled `.nii` or `.nii.gz` scans in the input directory (following the subject/session/anat path) 
and runs the job submission script for each scan to generate PNGs.

	Inputs arguments :
	`-i` (required): Path to the input BIDS directory
	`-o` (required): Full path to the output directory for QC PNG storage
	`-d` (optional): Full path to the directory containing sysnthseg outputs

	Output :
	if `-d` is provided :
		sbatch jobSingleScanSynthsegPngGenerator.sh <scanPath> <outBase> <scanDer>
	else :
		sbatch jobSingleScanPngGenerator.sh <scanPath> <outBase>

"""

import glob
import pandas as pd
import sys
import os
import argparse
import json

# Main function
def main():
    # --- Set up the argument parser ---
    parser = argparse.ArgumentParser()
    # Add an argument to get the directory of scans to generate PNGs from
    parser.add_argument('-i', '--input-dir', help='Full path to the input BIDS directory', required = True)
    # Add an argument to get the directory where the QC PNGs will be written
    parser.add_argument('-o', '--output-dir', help='Path to output directory for QC PNG storage', required = True)
    # Add an optional argument to get the derivatives directory for synthseg overlay PNGs --> Optional!
    parser.add_argument('-d', '--der-dir', help='Full path to the synthseg derivatives directory ')
    # Add an optional argument to inidcate that the BIDS scans underwent ACPC alignment
    parser.add_argument('-p', '--preprocessed', help="Flag whose presence indicates the BIDS scans were preprocessed using ACPC alignment", action='store_false')
 
    # Parse the arguments
    args = parser.parse_args()
    inDir = args.input_dir
    outBase = args.output_dir
    derivatives = args.der_dir
    isPreprocessed = args.preprocessed

    # If the output directory doesn't exist, create it
    if not os.path.exists(outBase):
        os.makedirs(outBase)

    # --- For all of the subjects in the input directory ---
    # Get a list of subject IDs 
    subIDs = [sub for sub in os.listdir(inDir) if "sub-" in sub]
    
    for subID in subIDs:
        # Full path to subject directory
        subPath = os.path.join(inDir, subID)
        # List of sessions
        sesIDs = [ses for ses in os.listdir(subPath) if "ses-" in ses]
        
        # --- For every session belonging to a single subject ---
        for sesID in sesIDs:
           sesPath = os.path.join(subPath, sesID)
           anatPath = os.path.join(sesPath, "anat")
           
           # Check if session has anat folder
           if not os.path.exists(anatPath):
               continue
           # Get the list of niftis in the anat folder
           # TODO: generalize for more than MPR labeled scans
           scans = [scan for scan in os.listdir(anatPath) if (".nii" in scan) and ("MPR" in scan)]
          
           # --- For every anat scan in that session for the subject ---
           for scan in scans:
               scanPath = os.path.join(anatPath, scan)
               scanID = scan.split(".nii")[0]
               # Submit the job here
               if derivatives is not None:
                  scanDer = os.path.join(derivatives, scanID, scanID+"_synthseg.nii.gz")
                  if os.path.exists(scanDer):
                     cmd = 'sbatch jobSingleScanSynthsegPngGenerator.sh '
                     cmd += scanPath + ' ' + outBase + ' ' + scanDer + ' ' + str(isPreprocessed)
                     os.system(cmd)
                     print("Submitted job for : ", scanID)
                     print()
                  else:
                     print("!! Segmentation output does not exist for scan : ", scanID)
                     print()
                     
               else:
                  cmd = 'sbatch jobSingleScanPngGenerator.sh '
                  cmd += scanPath + ' ' + outBase + ' ' + str(isPreprocessed)
                  os.system(cmd)
                  print("Submitted job for : ", scanID)
                  print()
         

if __name__ == "__main__":
    main()
    print("The PNG generation jobs have been submitted")
