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
    if os.path.exists(ratingDfFn):
        ratingDf = pd.read_csv(ratingDfFn)
    # If the rating file doesn't exist, set up the columns
    else:
        setup = {"batch": [batch for i in range(len(fns))],
                "png_filename": fns, 
                "subject": [i.split("_")[0] for i in fns], 
                "session": [i.split("_")[1] for i in fns],  
                "rater": [raterName for i in range(len(fns))], 
                "rater_grades": [np.nan for i in range(len(fns))]}
        ratingDf = pd.DataFrame(setup)
        
    return viewFnsDict, ratingDf

##
# Rate the pngs for a single view
# @param viewFs
