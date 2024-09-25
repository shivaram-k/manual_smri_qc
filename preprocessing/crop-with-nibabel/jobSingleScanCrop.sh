#!/bin/bash
#SBATCH --job-name=png-generation-prepoc
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=%x_%j.out

# -------------------------------------------
# This script submits a job to run crop.py on the input scan. 
# It is used internally by runBrainCrop.py.

#	Input arguments :
#	`WRKDIR` : Working directory
#   `INFN` : Input scan
#   `OUTFN` : Output scan path

# -------------------------------------------

INFN=$1   # Input scan path
OUTFN=$2    # Output scan path


python crop.py $INFN $OUTFN

# Done!

