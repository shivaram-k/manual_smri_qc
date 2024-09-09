#!/bin/bash 
#set -e

# Requirements for this script
#  installed versions of: FSL (version 5.0.6) (including python with numpy, needed to run aff2rigid - part of FSL)
#  environment: FSLDIR

################################################ SUPPORT FUNCTIONS ##################################################

Usage() {
  echo "`basename $0`: Tool for cropping the scan without ACPC alignment"
  echo " "
  echo "Usage: `basename $0` --workingdir=<working dir> --in=<input image> --out=<output image> [--brainsize=<brainsize>]"
}

# function for parsing options
getopt1() {
    sopt="$1"
    shift 1
    for fn in $@ ; do
	if [ `echo $fn | grep -- "^${sopt}=" | wc -w` -gt 0 ] ; then
	    echo $fn | sed "s/^${sopt}=//"
	    return 0
	fi
    done
}

defaultopt() {
    echo $1
}

################################################## OPTION PARSING #####################################################

# Just give usage if no arguments specified
if [ $# -eq 0 ] ; then Usage; exit 0; fi
# check for correct options
if [ $# -lt 3 ] ; then Usage; exit 1; fi

# parse arguments
WD=`getopt1 "--workingdir" $@`  # "$1"
Input=`getopt1 "--in" $@`  # "$2"
Output=`getopt1 "--out" $@`  # "$3"
BrainSizeOpt=`getopt1 "--brainsize" $@`  # "$4"

# default parameters
Output=`$FSLDIR/bin/remove_ext $Output`
WD=`defaultopt $WD ${Output}.wdir`

# make optional arguments truly optional  (as -b without a following argument would crash robustfov)
if [ X${BrainSizeOpt} != X ] ; then BrainSizeOpt="-b ${BrainSizeOpt}" ; fi

echo " "
echo " START: Cropping without ACPC alignment"

mkdir -p $WD

# Record the input options in a log file
echo "$0 $@" >> $WD/log.txt
echo "PWD = `pwd`" >> $WD/log.txt
echo "date: `date`" >> $WD/log.txt
echo " " >> $WD/log.txt

########################################## DO WORK ########################################## 

# Crop the FOV
${FSLDIR}/bin/robustfov -i "${Input}" -m "$WD"/roi2full.mat -r "$WD"/robustroi.nii.gz $BrainSizeOpt

# Invert the matrix (to get full FOV to ROI)
${FSLDIR}/bin/convert_xfm -omat "$WD"/full2roi.mat -inverse "$WD"/roi2full.mat

# Create final cropped image
${FSLDIR}/bin/flirt -interp nearestneighbour -in "$WD"/robustroi.nii.gz -ref "${Input}" -applyxfm -init "$WD"/roi2full.mat -out "${Output}"

echo " "
echo " END: Cropping"
echo " END: `date`" >> $WD/log.txt

##############################################################################################
