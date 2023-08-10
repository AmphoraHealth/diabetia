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
from conf.global_constants import *

# Constants -------------------------------------------------------------------
IN_PATH = f"{AUX_ORIGIN_DATABASE}"
FOLD_PATH = f"{S00_FOLD_SPLITING}.json"
NORM_PATH = f"{S02_NORMALIZATION}.json"
STD_PATH = f"{S02_NORMALIZATION.replace('normalized', 'scaled')}.json"
FEAT_PATH = f"{S03_FEATURE_SELECTION}.json"
MODEL_PATH = f"{S04_MODEL_TRAIN}.pkl"

OUT_PATH = f"{S05_PREDICTION}.csv"

# Import libraries ------------------------------------------------------------
from sklearn.metrics import balanced_accuracy_score
import pandas as pd
import pickle
import json

# Code: prediction ------------------------------------------------------------
# general code for prediction on the test fold
#   taking into account the selected diagnostic, test_fold, selection_method and model

# Load data
df = pd.read_csv(IN_PATH)
with open(FOLD_PATH) as f:
  fold_selection = json.load(f)

# get the ids of the test fold and filter the data
ids = fold_selection[str(TEST_FOLD)]["ids"]
df = df.loc[df["id"].isin(ids)]

# normalize the data

# load features
features = json.load(open(FEAT_PATH, "r", encoding="UTF-8"))["columns"]

# load the model
logging.info(f"loading model from {MODEL_PATH}")
with open(MODEL_PATH, "rb") as f:
  m = pickle.load(f)

# predict
pred = m.predict(df[features])
real = df[DIAGNOSTIC]

# print the model balanced accuracy
logging.info(f"model test accuracy: {balanced_accuracy_score(real, pred)}")

# save the prediction in a csv
df = pd.DataFrame({"id":ids, "real":real, "pred":pred})
df.to_csv(OUT_PATH, index=False)
