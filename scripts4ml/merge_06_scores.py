""" merge_06_scores.py
    This file contains the code for merging the scores by fold into a single file.
"""
import pandas as pd
import glob

# Get a list of files to merge using glob and a wildcard
files = glob.glob("data/ml_data/06_score-0-e112-*.csv")

# Load the dataframes
dfs = [pd.read_csv(file) for file in files]

# To each dataframe, add a column with the filename and remove the fold column
for i, df in enumerate(dfs):
  df["filename"] = files[i].split("/")[-1]
  df.drop("fold", axis=1, inplace=True)

# Concatenate the dataframes
df = pd.concat(dfs, ignore_index=True)

# extract the source from the filename
df["source"] = df["filename"].apply(lambda x: x.split("-")[3])

# extract the balancing method from the filename
df["balancing_method"] = df["filename"].apply(lambda x: x.split("-")[4])

# extract the normalization method from the filename
df["normalization_method"] = df["filename"].apply(lambda x: x.split("-")[5])

# extract the standardization method from the filename
df["standardization_method"] = df["filename"].apply(lambda x: x.split("-")[6])

# extract the feature selection method from the filename
df["feature_selection_method"] = df["filename"].apply(lambda x: x.split("-")[7])

# extract the machine learning model from the filename
df["machine_learning_model"] = df["filename"].apply(lambda x: x.split("-")[8].split(".")[0])

# remove the filename column and reorder the columns
df.drop("filename", axis=1, inplace=True)
cols = df.columns.tolist()
cols = cols[-6:] + cols[:-6]
df = df[cols]

# sort by balanced accuracy, f1 score and roc
df.sort_values(by=["balanced_accuracy", "f1", "roc"], ascending=False, inplace=True)

# Save the dataframe
df.to_csv("data/ml_data/merged_06_scores-0-e112.csv", index=False)