#!/bin/bash
#SBATCH --job-name=png-generation
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=%x_%j.out

# -------------------------------------------
# This script submits a job to run singleScanPngGenerator.py on the input scan, creating structural PNGs. 
# It is used internally by runPngGenerator.py.

#	Input arguments :
#	`INFN` : Path to input scan
#	`OUTDIR` : Path to output directory

# -------------------------------------------


INFN=$1      # file name
OUTDIR=$2    # output directory for PNGs
PREPROC_STATUS=$3

# Set up conda
source ${HOME}/miniconda3/etc/profile.d/conda.sh
conda activate nilearn

# if $PREPROC_STATUS 
time python singleScanPngGenerator.py -f $INFN -o $OUTDIR -p

# Done!
echo "Job finished running!"


