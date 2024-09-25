#!/bin/bash
#SBATCH --job-name=png-generation-prepoc
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=%x_%j.out

# -------------------------------------------
# This script submits a job to run crop_scan.sh on the input scan. 
# It is used internally by runCrop.py.

#	Input arguments :
#	`WRKDIR` : Working directory
#       `INFN` : Input scan
#       `OUTFN` : Output scan path


# -------------------------------------------

WRKDIR=$1   # Working directory
INFN=$2     # Input scan
OUTFN=$3    # Output scan path


# Load the fsl module
module load fsl

bash crop_scan.sh --workingdir=$WRKDIR --in=$INFN  --out=$OUTFN 


# Done!
echo "Job finished running!"
