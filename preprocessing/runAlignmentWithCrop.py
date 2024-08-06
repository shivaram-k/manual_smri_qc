
"""
This script currently looks for anat MPR labeled `.nii` or `.nii.gz` scans in the input directory (following the subject/session/anat path) 
and runs the job submission script for each scan to preprocess the scans with ACPC alignment and cropping.

    Input arguments :
    `-i` (required): Full path to the input BIDS directory
    `-o` (required): Full path to the output directory for preprocessed scans
    `-s` (required): Full path to the scratch directory for intermediate files

    Output:
    Submits jobs for preprocessing each scan:
        sbatch jobSingleScanPrepoc.sh <scanWorkingDir> <scanPath> <newScanPath> <omat>
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
    # Add an argument to get the directory where the preprocessed scans will be written
    parser.add_argument('-o', '--output-dir', help='Path to output directory for preprocessed scans', required = True)
    # Add an argument to get the scratch directory where intermediate files will be stored. On Respublica, this could be : /scr1/users/<user>
    parser.add_argument('-s', '--scratch-dir', help='Path to the scratch directory where intermediate files will be stored. On Respublica, this could be : /scr1/users/<user>', required = True)
 
    # Parse the arguments
    args = parser.parse_args()
    inDir = args.input_dir
    outBase = args.output_dir
    scrDir = args.scratch_dir

    outDir = os.path.join(outBase, 'BIDS-preprocessed')
    # If the output directory doesn't exist, create it
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    # Copy participants files to the new BIDS directory
    cp_tsv = 'cp ' + os.path.join(inDir, 'participants.tsv') + ' ' + outDir
    cp_json = 'cp ' + os.path.join(inDir, 'participants.json') + ' ' + outDir
    os.system(cp_tsv)
    os.system(cp_json)

    # Working directory for acpc alignment and cropping 
    workingDir = os.path.join(scrDir, 'PNG_preprocessing')
    # Create the working directory
    if not os.path.exists(workingDir):
        os.makedirs(workingDir)

    # module load fsl
    #os.system('module load fsl')
    fslDir = os.getenv('FSLDIR')

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
            # TODO: generalize for more than MPR labeled scans. This would also change the --ref argument for ACPC alignment
            scans = [scan for scan in os.listdir(anatPath) if (".nii" in scan) and ("MPR" in scan)]
          
            # --- For every anat scan in that session for the subject ---
            for scan in scans:
                scanPath = os.path.join(anatPath, scan)
                scanID = scan.split(".nii")[0]

                preproc_script_path = os.path.join(os.path.dirname(__file__), 'ACPCAlignment_with_crop.sh')
                scanWorkingDir = os.path.join(workingDir, subID, sesID, 'anat', scanID)
                newScanPath = os.path.join(outDir, subID, sesID, 'anat')
                # Create the new scan path directories
                if not os.path.exists(newScanPath):
                    os.makedirs(newScanPath)
                newScanPath = os.path.join(newScanPath, scan)
                omat = os.path.join(workingDir, 'output_matrix.mat')

                # Submit the job here
                cmd = 'sbatch jobSingleScanPrepoc.sh '
                cmd += scanWorkingDir + ' ' + scanPath + ' ' + newScanPath + ' ' + omat
                os.system(cmd)
                print("Submitted job for : ", scanID)
                print()
         

if __name__ == "__main__":
    main()
    print("The preprocessing jobs have been submitted")
