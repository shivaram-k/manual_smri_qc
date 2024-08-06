The purpose of this tool is to generate a set of 9 views for each of a set of nifti scans and provide an interface for manually grading the quality of each scan.

### I. Set up your local environment

This repo requires the `nilearn` Python library (among others). To set up your environment to support this code, follow the following steps:

#### Option 1 : Create the environment from nilearn_env.yml 
```
conda env create -f nilearn_env.yml
conda activate nilearn
```

#### Option 2 : Manually create it using conda and pip
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
### II. Preprocessing (ACPC alignment and cropping)

To perform ACPC alignment and cropping of MRI images, run the following commands :
```
cd preprocessing
python runAlignmentWithCrop.py -i /path/to/input/BIDS -o /path/to/output/base/directory -s /scr1/users/<user>
```
Example - 
```
 python  runAlignmentWithCrop.py -i /mnt/isilon/bgdlab_processing/Data/SLIP/slip_vsmol/BIDS 
						-o /mnt/isilon/bgdlab_processing/Data/SLIP/slip_vsmol
						-s /scr1/users/myusernmame
```
This results in the following output:

1. `/mnt/isilon/bgdlab_processing/Data/SLIP/slip_vsmol/BIDS-preprocessed`: ACPC Aligned and cropped scans organized in the BIDS format. This directory should be the input for the next step.
2. `/scr1/users/myusernmame/PNG-preprocessing`: Directory with intermediate files in the scratch space provided. Can be deleted once the jobs are completed.

### III. PNG Generation

To generate PNGs for MPRs in a BIDS directory, run the following commands :
```
conda activate nilearn
cd png-generation
python runPngGenerator -i /path/to/input/BIDS -o /path/to/output/directory [-d /path/to/synthseg/outputs/directory]
```

Example - 
```
 python  runPngGenerator.py -i /mnt/isilon/bgdlab_processing/Data/SLIP/slip_vsmol/BIDS 
						-o /home/<user>/QC 
						-d /mnt/isilon/bgdlab_processing/Data/SLIP/slip_vsmol/derivatives/synthseg+_robust_parc
```
This results in the following output:

1. `/home/<user>/QC`: Structural PNGs organized in subdirectories named after their respective scan names.
2. `/home/<user>/QC_SS_Overlays`: (Structural + Synthseg overlay) PNGs, organized in subdirectories named after their respective scan names.
### GIF Generation

Todo : add documentation

### For the next two steps, use the code files in the `grading-new` folder.
### IV. Generate PNG batches

Divide the PNGs into batches that are expected to take about 15 minutes to grade. Assuming 5 seconds to examine each set of 3 PNGs in the same view and 3 views per scan, it should take less than 1 minute to grade each scan.
- For structural PNGs :
```
python generatePngBatches.py -i /path/to/input/png/directory -p /path/to/participants.tsv -u ageUnits -o /path/to/the/output/base/directory
```

Example - 
```
 python generatePngBatches.py -i /home/<user>/QC -p /mnt/isilon/bgdlab_processing/Data/SLIP/slip_vsmol/BIDS/participants.tsv -u m -o /home/<user>
```

- For (Structural + Synthseg overlay) PNGs :
```
python generatePngBatches.py -i /path/to/input/png/directory -s -p /path/to/participants.tsv -u ageUnits -o /path/to/the/output/base/directory
```

Example - 
```
 python generatePngBatches.py -i /home/<user>/QC_SS_Overlays -s -p /mnt/isilon/bgdlab_processing/Data/SLIP/slip_vsmol/BIDS/participants.tsv -u m -o /home/<user>
```

### V. Grading Notebook

Run the cells and proceed as directed.
