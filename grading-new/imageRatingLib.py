
"""
Custom library used by the Grading notebook to display PNGs per batch.
"""

from IPython.display import display, HTML
from PIL import Image
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random
from IPython.display import clear_output
import csv

# Function to get user input
def get_user_input(prompt):
    while True:
        user_input = input(prompt).strip()
        confirmation = input(f"You entered '{user_input}'. Is this correct? (yes/no): ").strip()
        
        while True:
            try:
                confirmation = confirmation.lower()
            except:
                print("Invalid input")

            if confirmation in ['yes', 'no']:
                break
            else:
                confirmation = input(f"You entered '{user_input}'. Is this correct? (yes/no): ").strip()
        if confirmation == 'yes':
            return user_input
        else:
            print("Let's try again.")


# Function to check if grader is in the database
def check_grader(gradersCSV, grader_name):

    with open(gradersCSV, 'r', newline='') as csvfile:
        for line in csvfile:
            if line.strip().lower().replace(' ', '_') == grader_name:
                return True
    return False

# Function to add a new grader to the database
def add_grader(gradersCSV, grader_name, qc_files):

    # Step 1: Add grader to the CSV file
    with open(gradersCSV, 'a') as csvfile:
        csvfile.write(grader_name + '\n')
        
    # Step 2: Create a directory for the grader if it doesn't exist
    grader_dir = os.path.join(qc_files, grader_name)
    if not os.path.exists(grader_dir):
        os.makedirs(grader_dir)
        
        # Copy batch TSV files and add a column in each file to store grades
        for file_name in os.listdir(qc_files):
            if file_name.startswith('batch_') and file_name.endswith('.tsv'):
                # Read batch DataFrame from TSV file
                batch_df = pd.read_csv(os.path.join(qc_files, file_name), sep='\t')

                new_column_name = f'grade_{grader_name}'
                if new_column_name not in batch_df.columns:
                    # Add column for new grader to batch DataFrame
                    batch_df[new_column_name] = pd.NA

                    # Save modified batch DataFrame to TSV file in grader_dir
                    batch_df.to_csv(os.path.join(grader_dir, file_name), sep='\t', index=False)
        

# Function to get pending batches for a grader
def get_pending_batches(grader_name, qc_files):

    pending_batches = []
    for file_name in os.listdir(os.path.join(qc_files, grader_name)):
        if file_name.startswith('batch_') and file_name.endswith('.tsv'):
            batch_number = int(file_name.split('_')[1].split('.')[0])
            df = pd.read_csv(os.path.join(os.path.join(qc_files, grader_name), file_name), sep='\t')
            if (f'grade_{grader_name}' not in df.columns) or (df[f'grade_{grader_name}'].isna().any()):
                pending_batches.append(batch_number)
    return sorted(pending_batches)

# Function to get age_group to display in the notebook
def get_age_group(age_bin_num):
    
    # 0-1 month : bin number 1
    # 1-6 months: bin number 2
    # 6-12 months: bin number 3
    # 1-2 years: bin number 4
    # 2-5 years: bin number 5
    # 5-12 years: bin number 6
    # 12-50: bin number 7
    # 50+ : bin number 8
    
    if age_bin_num==1 :
        age_group = "0-1 month"
    elif age_bin_num==2 :
        age_group = "1-6 months"
    elif age_bin_num==3 :
        age_group = "6-12 months"
    elif age_bin_num==4 :
        age_group = "1-2 years"
    elif age_bin_num==5 :
        age_group = "2-5 years"
    elif age_bin_num==6 :
        age_group = "5-12 years"
    elif age_bin_num==7 :
        age_group = "12-50 years"
    elif age_bin_num==8 :
        age_group = "50+ years"
        
    return age_group

    
# Function to display batch for grading
def display_batch_for_grading(batch_number, grader_name, qc_files):

    file_name = f'batch_{batch_number:03d}.tsv'
    full_file_path = os.path.join(qc_files, grader_name, file_name)
    batch_df = pd.read_csv(full_file_path, sep='\t')
    grades = []
    for index, row in batch_df.iterrows():
        age_group = get_age_group(int(row["age_bin_num"]))
        print(f"Grading batch {batch_number} [Age group " , age_group ,"]:")
        img = Image.open(row["full_path"])
        scale = 2.5
        display(img.resize((int(img.width * scale), int(img.height * scale))))
        # ask for a rating
        rating = input("Grade the image on a scale of -1/0/2 (aka flag the image/poor quality/good quality) : ")

        while True:
            try:
                rating = int(rating)
            except:
                print("Invalid rating value.")

            if rating in [0, -1, 2]:
                break
            else:
                rating = input("Grade the image on a scale of -1/0/2 (aka flag the image/poor quality/good quality) : ")
                
        # Save the rating
        batch_df.at[index, f'grade_{grader_name}'] = rating
        print(list(batch_df))
        print(full_file_path)
        batch_df.to_csv(full_file_path, sep='\t', index=False)
        clear_output()


# Start the grading process
def start_grading():

    # Enter path to qc_files directory
    qc_files = get_user_input("Enter path to the qc_files or qc_files_synthseg directory : ")
    
    # Prompt grader to enter their name
    grader_name = get_user_input("Enter your name: ")
    grader_name = grader_name.lower().replace(' ', '_')

    # Check if grader is new or existing
    gradersCSV = os.path.join(qc_files, "registered_graders.csv")
    if not check_grader(gradersCSV, grader_name):
            add_grader(gradersCSV, grader_name, qc_files)
            print(f"Welcome {grader_name}! You have been added as a new grader.")
    else:
        print(f"Welcome back, {grader_name}!")
        
    # Get pending batches for the grader
    pending_batches = get_pending_batches(grader_name, qc_files)
    if not pending_batches:
        print("You have graded all the batches for this dataset.")
    else:
        for batch_number in pending_batches:
            display_batch_for_grading(batch_number, grader_name, qc_files)
            grade_more = input("Do you want to grade another pending batch? (y/n) : ").strip()
            
            while True:
                try:
                    grade_more = grade_more.lower()
                except:
                    print("Invalid input")

                if grade_more in ['y', 'n']:
                    break
                else:
                    grade_more = input("Do you want to grade another pending batch? (y/n) : ").strip()
            if grade_more == 'y':
                continue
            elif grade_more == 'n':
                break
        
        
        
        
