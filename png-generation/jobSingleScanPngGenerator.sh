#!/bin/bash
#SBATCH --job-name=png-generation
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=8G
#SBATCH --output=%x_%j.out

INFN=$1      # file name
OUTDIR=$2    # output directory for PNGs

#BASE=/mnt/isilon/bgdlab_resnas03/code/manual_smri_qc/
BASE=/home/gudapatis/SLIP_QC

# Set up conda
source ${HOME}/miniconda3/etc/profile.d/conda.sh
conda activate nilearn

time python $BASE/singleScanPngGenerator.py -f $INFN -o $OUTDIR 

# Done!
echo "Job finished running!"


