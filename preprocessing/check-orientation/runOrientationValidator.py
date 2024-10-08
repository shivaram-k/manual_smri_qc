
"""
This script currently looks for anat MPR labeled `.nii` or `.nii.gz` scans in the input directory (following the subject/session/anat path) 
and runs the job submission script for each scan to preprocess the scans by checking/reorienting the scans to LAS+.

    Input arguments :
    `-i` (required): Full path to the input BIDS directory
    `-o` (required): Full path to the output directory for preprocessed scans

    Output:
    Submits jobs for preprocessing each scan:
        sbatch jobSingleScanReorient.sh <inDir> <outDir>
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
    parser.add_argument('-o', '--output-dir', help='Path to output directory for reoriented scans', required = True)
 
    # Parse the arguments
    args = parser.parse_args()
    inDir = args.input_dir
    outBase = args.output_dir

    outDir = os.path.join(outBase, 'BIDS-reoriented')
    # If the output directory doesn't exist, create it
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    
    # Check for participants.tsv and participants.json
    partTSV = os.path.join(inDir, 'participants.tsv')
    partJSON = os.path.join(inDir, 'participants.json')
    
    if (not os.path.exists(partTSV)) or (not os.path.exists(partJSON)):
    	print("The input dataset is missing participants.json or participants.tsv")
    	sys.exit(1)
    	
    # Copy participants files to the new BIDS directory
    cp_tsv = 'cp ' + partTSV + ' ' + outDir
    cp_json = 'cp ' + partJSON + ' ' + outDir
    os.system(cp_tsv)
    os.system(cp_json)


    # module load fsl
    os.system('module load fsl')

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
            # TODO: generalize for more than MPR labeled scans. 
            scans = [scan for scan in os.listdir(anatPath) if (".nii" in scan) and ("MPR" in scan)]
            jsons = [scan for scan in os.listdir(anatPath) if (".json" in scan) and ("MPR" in scan)]
            
            zipped =  list(zip(scans, jsons))
          
            # --- For every anat scan in that session for the subject ---
            for scan,jsonf in zipped:
                scanPath = os.path.join(anatPath, scan)
                scanID = scan.split(".nii")[0]
                jsonPath = os.path.join(anatPath, jsonf)
                
                with open(jsonPath, 'r') as jfile:
                    data = json.load(jfile)
                    orientation = data["ImageOrientation"]
                    
                    if not orientation=="LAS+":
                        # If orientation is not LAS+ then reorient the scan and update json
                        
                        reorient_script_path = os.path.join(os.path.dirname(__file__), 'jobSingleScanReorient.sh')
                        dest_path = os.path.join(outDir, subID, sesID, 'anat')
                        # Create the dest_path directories
                        if not os.path.exists(dest_path):
                            os.makedirs(dest_path)
                        
                        # Change orientation in json and write to output directory
                        data["ImageOrientation"] = "LAS+"
                        new_json = os.path.join(dest_path, jsonf)
                        with open(new_json, 'w') as new_file:
                            json.dump(data, new_file, indent=4) 
                            
                        # Submit job to reorient scan
                        new_scan_path = os.path.join(dest_path, scan)
                        cmd = 'sbatch ' + reorient_script_path + ' '
                        cmd += scanPath + ' ' + new_scan_path
                        os.system(cmd)
                        print("Submitted job for : ", scanID)
                        print()
                        
                    else:
                        
                        # If orientation is LAS+ then copy-paste the scan and json to BIDS-reoriented
                        dest_path = os.path.join(outDir, subID, sesID, 'anat')
                        # Create the dest_path directories
                        if not os.path.exists(dest_path):
                            os.makedirs(dest_path)
                        
                        cp_scan = "cp " + scanPath + " " + dest_path
                        os.system(cp_scan)
                        
                        cp_json = "cp " + jsonPath + " " + dest_path
                        os.system(cp_json)
                    
         

if __name__ == "__main__":
    main()
    print("The preprocessing jobs have been submitted")
