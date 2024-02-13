The purpose of this tool is to generate a set of 9 views for each of a set of nifti scans and provide an interface for manually grading the quality of each scan.

Step 01: runPngGenerator.py

- Needs to be modified to include argparse command line arguments
- Currently operates on outputs of the FS/IFS pipeline, but only uses the registered and skull stripped version of the scan (no segmentations)
- For each anat scan in the specified BIDS directory, 
    - Determine if the scan would have been processed with FS or IFS based on patient age
    - Check that there are not already .PNG files for that scan
    - Pseudorandomly select 3 slices from each view (sagittal, axial, coronal) from around the 25%, 50%, and 75% slices of that view
    - Create a Freeview command to extract and save those slices as .PNGs
    - Kick off each Freeview command as a subprocess

Step 02: generatePngBatches.py

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

Step 03: Image QC Tool.ipynb

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
