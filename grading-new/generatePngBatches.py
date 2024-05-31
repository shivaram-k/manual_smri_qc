
"""

This script divides the input PNGs into ~15 minute batches that will be used by the grading notebook during grading.

	Inputs 
	`-i` : Path to input PNG directory
	`-s` : Flag indicating whether the input PNGs have synthseg output overlays
	`-p` : Path to the participants.tsv file
	`-u` : Units of age (accepted values : m, d, y)
	`-o` : Path to the output base directory where the 'qc_files' or 'qc_files_synthseg' directory, containing grading-related files, will be output
	
	
	Outputs
	qc_files or qc_files_synthseg directory with the following files :
	1. scan_batch_info.tsv : TSV file containing columns ["scan_name", "age_bin_num", "batch_num", "full_path"] 
	2. batch_{batch_num}.tsv : TSV files for each batch containing ["scan_name", "png_name", "age_bin_num", "batch_num", "full_path"]. (Lists the PNGs for every scan in each batch)
	3. registered_graders.csv : Empty CSV file to register and store graders' names.

"""


import os
import shutil
import random
import numpy as np
import argparse
import pandas as pd
import sys


# Check if participants.tsv contains specific column names: "subject_id", "session_id", and "age_at_scan"
def check_col_names(partDf):
	
	cols = partDf.columns
	if (not ("subject_id" in cols)) or (not ("session_id" in cols)) or (not ("age_at_scan" in cols)):
		sys.exit("Please change the column names in `participants.tsv` that contain subject id, \
		session id, and age to `subject_id`, `session_id`, and `age_at_scan`, then rerun the script.")
	else :
		return
	
# Get age in months from participants.tsv for a particular scan
def get_age(scanName, partDf, ageUnits):
	
	nameSplit = scanName.split("_")
	subject_id = nameSplit[0]
	session_id = nameSplit[1]
	
	partAge = partDf[(partDf["subject_id"] == subject_id) & (partDf["session_id"] == session_id)]["age_at_scan"].to_string(index=False)
	partAge = float(partAge)
	
	if ageUnits == "m":
		return partAge
		
	else:
		return convert_age_to_months(partAge, ageUnits)

# Convert age from days/years to months	
def convert_age_to_months(age, ageUnits):

	if ageUnits == "d":
		return (age/365.25)*12
		
	elif ageUnits == "y":
		return age * 12

# Get bin number for a given age
def get_age_bin_num(age):
	
	# 0-1 month : bin number 1
	# 1-6 months: bin number 2
	# 6-12 months: bin number 3
	# 1-2 years: bin number 4
	# 2-5 years: bin number 5
	# 5-12 years: bin number 6
	# 12-50: bin number 7
	# 50+ : bin number 8
	
	if age<=1 :
		ageBinNum = 1
	elif age>1 and age<=6 :
		ageBinNum = 2
	elif age>6 and age<=12 :
		ageBinNum = 3
	elif age>12 and age<=24 :
		ageBinNum = 4
	elif age>24 and age<=60:
		ageBinNum = 5
	elif age>60 and age<=144:
		ageBinNum = 6
	elif age>144 and age<=600:
		ageBinNum = 7
	elif age>600:
		ageBinNum = 8
		
	return ageBinNum 
	
	
def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--input-dir', help='Path to input PNG directory', required=True) 
	parser.add_argument('-s', '--synthseg', help='Generate batches for synthseg overlay PNGs', action='store_true')
	parser.add_argument('-p', '--participants', help='Path to the participants.tsv file', required=True)
	parser.add_argument('-u', '--age-units', help='Units of age (accepted values : m, d, y)', choices = ['m', 'd', 'y'],required=True)
	parser.add_argument('-o', '--output-dir', help='Path to the output base directory where the \'qc_files\' directory, containing grading-related files, will be output', required=True)
	
	# Parse arguments
	args = parser.parse_args()
	inDir = args.input_dir
	partPath = args.participants
	ageUnits = args.age_units
	outBase = args.output_dir
	synthseg = args.synthseg
	
	# Read participants file
	partDf = pd.read_csv(partPath, sep="\t")
	
	# Check column names for participants.tsv
	check_col_names(partDf)
	
	# Assuming 5 seconds per png and 9 pngs per scan, ~1 minute per scan
	# Keeping the batch to ~15 minute period
	numPngsPerBatch = 15 * 9  # units = pngs
	batch_size = int(numPngsPerBatch / 9) # Which is 15. This is the number of scans (each scan has 9 PNGs) per batch 
	
	# Get the path to the scans(sub directories) in the input directory
	inScans = os.listdir(inDir) # Each sub-directory in inScans has  9 PNGs
	
	print()
	
	#Number of batches required 
	numBatches = int(np.ceil(float(len(inScans)*9)/numPngsPerBatch))

	# Create a dataframe to store batch numbers for each scan
	batchesDf = pd.DataFrame(columns = ["scan_name", "age_bin_num", "batch_num", "full_path"], index = range(len(inScans)))
	batchesDf["scan_name"] = inScans
	
	# Populate age_bin_num and full_path columns
	for index,row in batchesDf.iterrows():
		batchesDf.at[index, "full_path"] = os.path.join(inDir, row["scan_name"])
		age = get_age(row["scan_name"], partDf, ageUnits)
		ageBinNum = get_age_bin_num(age)
		batchesDf.at[index, "age_bin_num"] = ageBinNum
		
	# Sort the df
	batchesDf.sort_values(by='age_bin_num', inplace=True)
	
	batchesDf["batch_num"] = 0
	current_batch = 1
	
	# Populate batch_number
	for age_bin, group in batchesDf.groupby('age_bin_num'):
        	for i in range(0, len(group), batch_size):
            		batchesDf.loc[group.index[i:i+batch_size], 'batch_num'] = current_batch
            		current_batch += 1

	if synthseg:
		outDir = os.path.join(outBase, "qc_files_synthseg")
	else:
		outDir = os.path.join(outBase, "qc_files")
	
	# Save the dataframe to batch_info.tsv
	if not os.path.exists(outDir):
		os.makedirs(outDir)
	outFn = os.path.join(outDir, "scan_batch_info.tsv")
	batchesDf.to_csv(outFn, index=False, sep="\t")
	
	# Divide main dataframe into batch dataframes
	batch_dfs = {}
	
	for batch_number, batch_data in batchesDf.groupby('batch_num'):
	
		batch_df_sub = pd.concat([pd.DataFrame({"scan_name": row["scan_name"],\
		"png_name": png, "age_bin_num": row["age_bin_num"], "batch_num": row["batch_num"],\
		"full_path": os.path.join(row["full_path"], png)}, \
		index=[0]) for _, row in batch_data.iterrows() for png in os.listdir(row["full_path"])], ignore_index=True)
		
		batch_dfs[batch_number] = batch_df_sub.reset_index(drop=True)

		
	# Save these to batch_{batch_num}.tsv files
	for batch_number, batch_df in batch_dfs.items():
		batch_outFn = os.path.join(outDir, "batch_" + str(batch_number).zfill(3)+".tsv")
		batch_df.to_csv(batch_outFn, index = False, sep="\t")
	
	# Add empty file to register graders
	gradersCSV = os.path.join(outDir, "registered_graders.csv")
	if not os.path.exists(gradersCSV):
		with open(gradersCSV, 'w'):
			pass  # No need to write anything



if __name__ == "__main__":
    main()
    
