""" prediction.py
    This file contains the code to predict the complication of a patient.

Input:
  - data/diabetia.csv
  - data/fold_selection-{complication}.json
  - data/features_selected-{complication}-{test_fold}.json
  - data/model-{complication}-{test_fold}.pkl
Output:
  - data/prediction-{complication}-{test_fold}.csv
  
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.logging import logging
from libs.global_constants import *

# Constants -------------------------------------------------------------------
IN_PATH = f"{AUX_ORIGIN_DATABASE}"
FOLD_PATH = f"{S00_FOLD_SPLITING}.json"
NORM_PATH = f"{S02A_NORMALIZATION}"
STD_PATH = f"{S02B_STANDARDIZATION}"
FEAT_PATH = f"{S03_FEATURE_SELECTION}.json"
MODEL_PATH = f"{S04_MODEL_TRAIN}.pkl"

OUT_PATH = f"{S05_PREDICTION}.parquet"

# Import libraries ------------------------------------------------------------
from sklearn.metrics import balanced_accuracy_score
from aux_00_common import *
import pandas as pd
import pickle
import json

# Code: prediction ------------------------------------------------------------
# general code for prediction on the test fold
#   taking into account the selected diagnostic, test_fold, selection_method and model
logging.info(f"{'='*30} prediction started")

# Load data
df = load_data(IN_PATH)
fold_selection = load_data(FOLD_PATH)

# get the ids of the test fold and filter the data
ids = fold_selection[str(TEST_FOLD)]["ids"]
df = df.loc[df["id"].isin(ids)]

# prepare normalization
cols = load_data(f"{NORM_PATH}.json")["columnsNormalized"]
norm = load_data(f"{NORM_PATH}.pkl")

# normalize the data
df[cols] = norm.transform(df[cols])

# prepare standardization
cols = load_data(f"{STD_PATH}.json")["columnsStandardized"]
std = load_data(f"{STD_PATH}.pkl")

# standardize the data
df[cols] = std.transform(df[cols])

# load features and filter the data
features = load_data(FEAT_PATH)["columns"]
df = df[["id"]+features+[DIAGNOSTIC]]

# load the model
logging.info(f"loading model from {MODEL_PATH}")
m = load_data(MODEL_PATH)

# predict
ids = df["id"]
pred = m.predict(df[features])
real = df[DIAGNOSTIC]

# print the model balanced accuracy
logging.info(f"model test accuracy: {balanced_accuracy_score(real, pred)}")

# save the prediction in a csv
df = pd.DataFrame({"id":ids, "real":real, "pred":pred})
save_data(df, OUT_PATH)

# final message
logging.info(f"{'='*30} prediction finished")