#!/bin/bash
#SBATCH --job-name=png-generation-reorient
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=%x_%j.out

# -------------------------------------------
# This script submits a job to run fsl2reorient2std on the input scan. 
# It is used internally by runOrientationValidator.py.

#	Input arguments :
#   `INFN` : Input scan
#   `OUTFN` : Output scan path

# -------------------------------------------

INFN=$1   # Input scan path
OUTFN=$2    # Output scan path


# Load fsl
module load fsl

# Reorient the image
${FSLDIR}/bin/fslreorient2std $INFN $OUTFN
