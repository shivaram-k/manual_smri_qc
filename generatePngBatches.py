import os
import shutil
import random

# Variables to change
baseDir = "/Users/youngjm/Data/clip/images/qc/mpr_fs_6.0.0/"
# Assuming 5 seconds per png and 9 pngs per scan, ~1 minute per scan
# Keeping the batch to ~30 minute period, want 30 scans per batch
numPngsPerBatch = 9*30 

# Get the paths for the images 
imgs = sorted(os.listdir(baseDir+"pngs/"))
imgs = [ i for i in imgs if "sub" in i ]

# Get the subjects with session ids from the list of images
subjects = list(set([i.split("_dim")[0] for i in imgs]))
random.shuffle(subjects)

# Set up variables
batchFiles = []
assignedSubjects = []
# Assumption: batch generation is done once and is not expected to resume from a previous state
batchId = 1
subjIdx = 0

# while there are subjects who have not been assigned to a batch
while len(assignedSubjects) < len(subjects):
    # fill a batch with subject pngs
    print("batch start")
    # While there are still spaces left in the batch and scans left to assign
    while len(batchFiles) < numPngsPerBatch and subjIdx < len(subjects):
        if subjects[subjIdx] not in assignedSubjects:
            print(subjects[subjIdx])
            # Get the ids of the scans belonging to the subject
            subjImgs = [baseDir+"pngs/"+i for i in imgs if subjects[subjIdx] in i]
        
            # Check that there are 9 pngs for the subject
            assert(len(subjImgs) == 9)
    
            # Add the images for that subject to the list of images for the batch
            batchFiles.extend(subjImgs)   
            assignedSubjects.append(subjects[subjIdx])

            # Increment the subject idx
            subjIdx += 1

    # When the batch is full
    # move the files from baseDir + png/ to baseDir + batc - how am I keeping track of batch ids? Maybe each batch gets 2 4 digit ids? batch_0000_0001 
    outDir = baseDir+"batch_0000_"+str(batchId).zfill(4)+"/"
    print(outDir)
    # If the outdir doesn't exist make it
    if not os.path.exists(outDir):
        os.mkdir(outDir)
    # Copy files over to the batch directory
    for fn in batchFiles:
        print(fn)
        newFn = outDir + fn.split("/")[-1]
        shutil.copyfile(fn, newFn)
    # Reset variables for next batch
    batchFiles = []
    batchId += 1
        

