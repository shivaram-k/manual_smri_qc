The purpose of this tool is to generate a set of 9 views for each of a set of nifti scans and provide an interface for manually grading the quality of each scan.

### Step 00: Set up your local environment

This repo requires the `nilearn` Python library (among others). To set up your environment to support this code, follow the following steps:

```
conda create -n nilearn python=3.9
conda activate nilearn
python -m pip install -U nilearn
conda install conda-forge::nibabel
conda install scikit-learn
```

If you encounter errors when trying to load `nilearn`, you may also need to run the following commands:

```
pip install pyyaml
pip install urllib3=1.25.4
```

Additionally, the following libraries may be useful for debugging purposes: 

```
conda install jupyter
pip install chardet
conda install matplotlib
```

### Step 01: runPngGenerator.py

This script takes two command line arguments:

- `--input-dir`: The path to the BIDS directory containing subject/session/anat/image.nii.gz files
- `--output-dir`: The path that will contain the directories of PNGs for QC after the script is run.

The script currently looks for raw MPR labeled .nii or .nii.gz scans in the input directory (following the subject/session/anat path), pseudorandomly identified 3 slices from around the 25th, 50th, and 75th centiles of the image data in each dimension, and saves them as PNG files in the output directory.

### Step 02: generatePngBatches.py

Updates have left off here.

- Divide the PNGs for each scan into batches that are expected to take 30 minutes to grade. Assuming 5 seconds to examine each set of 3 PNGs in the same view and 3 views per scan, it should take less than 1 minute to grade each scan. 
- Previous documentation indicates that grading 30 scans took about 9 minutes
- One of the concerns with manual grading is making sure different demographic groups (ie, age) are adequately distributed between the grading batchs
- For a set of PNGs
    - Determine how many batches are needed
    - Divide subjects into age groups
    - Split the age groups into sets of X PNGs per batch
    - Note: all PNGs for a single scan should be in the same batch
- For each batch
    - Grab a random set of PNGs from each age group
    - Put the files in a directory labelled by batch number

### Step 03: Image QC Tool.ipynb

This step will eventually be migrated to Brain Swipes

- First cell: Each grader must change the rater name to the name they would like to be used in any future publications
- Second cell:
    - If the grader has not manually rated scans before, a .csv file will be generated to hold their ratings and the order of the batches will be randomly shuffled to reduce bias.
    - For a single batch,
        - The 3 PNG views from one scan will be displayed. 
        - The grader will be asked to rate the quality of the scan based on those views (see PNC manual qc documentation).
    - When all PNGs in a batch are graded, the batch will be marked as complete in the grader's .csv file
- Third cell:
    - Check that all of the scans in the grader's batches have been graded
    - Print a status update
