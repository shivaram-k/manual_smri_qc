import os
import random

# Variables to change
baseDir = "/home/jenna/CHOP/png_testing/"
numScansPerBatch = 9

# Get the paths for the images 
imgs = sorted(os.listdir(baseDir+"pngs/"))

# Get the subjects from the list of images
subjects = list(set([i.split("_")[0] for i in imgs]))
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
    print(" batch start")
    while len(batchFiles) < numScansPerBatch:
        print(assignedSubjects)
        if subjects[subjIdx] not in assignedSubjects:
            print(subjects[subjIdx])
            # Get the ids of the scans belonging to the subject
            subjImgs = [baseDir+"pngs/"+i for i in imgs if subjects[subjIdx] in i]
        
            # Check that there are 9 pngs for the subject
            assert(len(subjImgs) == 9)
    
            # Add the images for that subject to the list of images for the batch
            batchFiles.extend(subjImgs)   # move the files into the batch folder
            print(batchFiles)
            assignedSubjects.append(subjects[subjIdx])

            # Increment the subject idx
            subjIdx += 1

    # When the batch is full
    # move the files from baseDir + png/ to baseDir + batc - how am I keeping track of batch ids? Maybe each batch gets 2 4 digit ids? batch_0000_0001 
    outDir = baseDir+"batch_0000_"+str(batchId).zfill(4)+"/"
    # print stuff
    print(outDir)
    print(batchFiles)
    print(batchId)
    # If the outdir doesn't exist make it
    # Copy or move....
    # Reset variables for next batch
    batchFiles = []
    batchId += 1
        

