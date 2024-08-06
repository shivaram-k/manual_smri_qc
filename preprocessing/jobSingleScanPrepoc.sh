#!/bin/bash
#SBATCH --job-name=png-generation-prepoc
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=%x_%j.out

# -------------------------------------------
# This script submits a job to run ACPCAlignment_with_crop.sh on the input scan. 
# It is used internally by runAlignmentWithCrop.py.

#	Input arguments :
#	`WRKDIR` : Working directory
#   `INFN` : Input scan
#   `OUTFN` : Output scan path
#   `OMAT` : Output matrix

# -------------------------------------------

WRKDIR=$1   # Working directory
INFN=$2     # Input scan
OUTFN=$3    # Output scan path
OMAT=$4     # Output matrix


# Load the fsl module
module load fsl

bash ACPCAlignment_with_crop.sh --workingdir=$WRKDIR --in=$INFN  --out=$OUTFN --omat=$OMAT --ref="${FSLDIR}/data/standard/MNI152_T1_1mm.nii.gz"


# Done!
echo "Job finished running!"