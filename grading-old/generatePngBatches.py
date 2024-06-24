import os
import shutil
import random
import numpy as np

# Variables to change
baseDir = "/Users/youngjm/Data/clip/images/qc/mpr_fs_6.0.0/"
# Assuming 5 seconds per png and 9 pngs per scan, ~1 minute per scan
# Keeping the batch to ~30 minute period, want 30 scans per batch
# After modifying the qc tool to show all 3 scans from the same view at once, the previous batch size (9*30) took 9 minutes
#   As a result, multiplying by 3
numPngsPerBatch = 9*30*3  # units = pngs

# Get the paths for the images 
imgs = sorted(os.listdir(baseDir+"pngs/"))
imgs = [ i for i in imgs if "sub" in i ]

# Get the number of batches needed
numBatches = int(np.ceil(float(len(imgs))/numPngsPerBatch))

# Get the subjects with session ids from the list of images
subjects = list(set([i.split("_dim")[0] for i in imgs]))

# Separate subjects out into age groups
group0to2 = []
group2to5 = []
group5to10 = []
group10up = []

for s in subjects:
    # Get the age in days
    age = int(s.split("age")[-1])

    if age < (365.25*2):
        group0to2.append(s)
    elif age < (365.25*5):
        group2to5.append(s)
    elif age < (365.25*10):
        group5to10.append(s)
    else:
        group10up.append(s)

# Shuffle the subject groups
random.shuffle(group0to2)
random.shuffle(group2to5)
random.shuffle(group5to10)
random.shuffle(group10up)

# Divide each group into the number of batches
batches0to2 = np.array_split(np.array(group0to2), numBatches)
batches2to5 = np.array_split(np.array(group2to5), numBatches)
batches5to10 = np.array_split(np.array(group5to10), numBatches)
batches10up = np.array_split(np.array(group10up), numBatches)

print(batches0to2)

# Populate the batches
for i in range(numBatches):
    # Get the scan ids for the batch
    scanIds = list(batches0to2[i]) + list(batches2to5[i]) + list(batches5to10[i]) + list(batches10up[i])

    # Generate a complete list of files for the batch
    batchFiles = []

    for scanId in scanIds:
        scanPngs = [baseDir + "pngs/" + j for j in imgs if scanId in j]
        assert(len(scanPngs) == 9)
        batchFiles.extend(scanPngs)

    # The batch is full after this line
    # move the files from baseDir + png/ to baseDir + batch 
    outDir = baseDir+"batch_"+str(i+1).zfill(4)+"/"
    # If the outdir doesn't exist make it
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    # Copy files over to the batch directory
    for fn in batchFiles:
        newFn = outDir + fn.split("/")[-1]
        shutil.copyfile(fn, newFn)

