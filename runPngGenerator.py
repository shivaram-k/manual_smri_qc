import glob
import pandas as pd
import sys
import os
import argparse
import json

##
# Main function
def main():
    # --- Set up the argument parser ---
    parser = argparse.ArgumentParser()
    # Add an argument to get the directory of scans to generate PNGs from
    parser.add_argument('-i', '--input-dir', help='Path to and including input BIDS directory')
    # Add an argument to get the directory where the QC PNGs will be written
    parser.add_argument('-o', '--output-dir', help='Path to output directory for QC PNG storage')
 
    # Parse the arguments
    args = parser.parse_args()
    inDir = args.input_dir
    outBase = args.output_dir

    # If the output directory doesn't exist, create it
    if not os.path.exists(outBase):
        os.makedirs(outBase)
        
    # --- Read participants.tsv ---
    demoPath = os.path.join(inDir, "participants.tsv")
    
    # Exit if participants.tsv not present
    if not os.path.exists(demoPath):
        print("Not a valid BIDS directory. Missing participants.tsv")
        sys.exit(1)

    demoDf = pd.read_csv(demoPath, sep="\t")
    
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
           scans = [scan for scan in os.listdir(anatPath) if ".nii" in scan and "MPR" in scan]
          
           # --- For every anat scan in that session for the subject ---
           for scan in scans:
               scanPath = os.path.join(anatPath, scan)
               # Submit the job here
               cmd = 'sbatch jobSingleScanPngGenerator.sh '
               cmd += scanPath + ' ' + outBase
               os.system(cmd)

if __name__ == "__main__":
    main()
    print("The PNG generation jobs have been submitted")
