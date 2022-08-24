from IPython.display import display, HTML
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from IPython.display import clear_output

##
# Get the ID of the next batch for the specified user to rate 
# @param raterName A str with the rater's first and last name
# @param baseDir A str containing the full path to the directory containing the batches of pngs to grade
# @return batchOrderFn A str containing the full path to the file containing the batch grading order for the specified rater
# @return nextBatch A str specifying the next batch for the user to grade
def getBatchId(raterName, baseDir):
    # Get the batch order file for the rater
    batchOrderFn = baseDir + "rater_batches_order/" + raterName.lower().replace(" ", "_")

    # Initial batch list generation
    if not os.path.exists(batchOrderFn):

        # Generate ordered list of batch ids
        batchList = [os.path.join(baseDir, i) for i in os.listdir(baseDir) if "batch_" in i]
        random.shuffle(batchList)

        # Set up the batch order dataframe
        batchStatusList = [False for batch in range(len(batchList))]
        batchStatusDf = pd.DataFrame({"batch_id": batchList,
                                      "batch_rating_complete": batchStatusList})
        batchStatusDf.to_csv(batchOrderFn)

    # Get the batch number of the next unrated batch
    batchStatusDf = pd.read_csv(batchOrderFn)
    nextBatch = batchStatusDf[batchStatusDf['batch_rating_complete'] == False]['batch_id'].values[0]
    return batchOrderFn, nextBatch

##
# Set up the environment for grading the specified batch of images
# @param baseDir A str containing the full path to the directory containing the batches of pngs to grade
# @param batch A str specifying the next batch for the user to grade
# @param ratingDfFn 
# @return
# @return A pandas Dataframe containing information about the ratings for the specified batch
def setBatchGrading(baseDir, batch, ratingDfFn, raterName):
    # List the file names
    fns = os.listdir(os.path.join(baseDir, batch))
    viewIds = list(set([i.split(".png")[0][:-4] for i in fns])) 
    # Shuffle the ids
    random.shuffle(viewIds)
    # Set up the list of viewFns and viewIds as a dictionary
    viewFnsDict = {}
    for viewId in viewIds:
        viewFnsDict[viewId] = [i for i in fns if viewId in i]
        
    
    # Check if the .csv to hold the image grades exists
    if not os.path.exists(ratingDfFn):
        setup = {"batch": [batch for i in range(len(fns))],
                "png_filename": fns, 
                "subject": [i.split("_")[0] for i in fns], 
                "session": [i.split("_")[1] for i in fns],  
                "rater": [raterName for i in range(len(fns))], 
                "rater_grades": [np.nan for i in range(len(fns))]}
        ratingDf = pd.DataFrame(setup)
        ratingDf.to_csv(ratingDfFn, index=False)

        
    return viewFnsDict

##
# Update batch status to completed
def markBatchAsComplete(batchOrderFn, nextBatch):
    batchStatusDf = pd.read_csv(batchOrderFn)
    batchStatusDf.loc[batchStatusDf['batch_id'] == nextBatch, 'batch_rating_complete'] = True
    batchStatusDf.to_csv(batchOrderFn, index=False)


##
# Rate the pngs for a single view
# @param viewFs
def rateBatchOfPngs(ratingDfFn, viewFnsDict, nextBatch, baseDir):
    ratingDf = pd.read_csv(ratingDfFn)
    # The scan rating counter = the number of the scan the user is currently rating
    scanRatingCounter = len(ratingDf[(ratingDf['batch'] == nextBatch) & (ratingDf['rater_grades'].notna())]['rater_grades'])+1
    # for each subject
    for scanView in viewFnsDict:
        # Get the filenames
        viewFns = viewFnsDict[scanView]
        # display progress
        print("Rating view " + str(scanRatingCounter) + " of " + str(len(viewFnsDict)) + " unique views")
        print("(FYI age at scan: approximately " +str(np.round(int(scanView.split("age")[-1].split('_')[0])/365.25, 2))+" years)")

        # load all 3 pngs
        img0 = plt.imread(os.path.join(os.path.join(baseDir, nextBatch), viewFns[0]))
        img1 = plt.imread(os.path.join(os.path.join(baseDir, nextBatch), viewFns[1]))
        img2 = plt.imread(os.path.join(os.path.join(baseDir, nextBatch), viewFns[2]))
        viewImg = np.concatenate([img0, img1, img2], axis=1)
        figsize = (len(viewImg)/10, len(viewImg[0])/20)
 
        display(HTML("<style>.container { width:100% !important; }</style>"))

        # display the png
        plt.figure(figsize=figsize)
        plt.imshow(viewImg)
        plt.show()

        # ask for a rating
        rating = ""
        while True:
            if rating in [0, 1, 2, -1]:
                break
            else:
                rating = input("Grade the image on a scale of 0/1/2/-1 (aka poor quality/not sure/good quality/not a precontrast brain image): ")

        # add the rating to the dataframe
        ratingDf.loc[ratingDf['png_filename'] == viewFns[0], 'rater_grades'] = rating
        ratingDf.loc[ratingDf['png_filename'] == viewFns[1], 'rater_grades'] = rating
        ratingDf.loc[ratingDf['png_filename'] == viewFns[2], 'rater_grades'] = rating

        scanRatingCounter += 1
        # clear the screen
        clear_output()
        # save the dataframe
        ratingDf.to_csv(ratingDfFn, index=False)
