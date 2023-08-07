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
from conf.global_constants import DIAGNOSTIC, ORIGIN, TEST_FOLD, BALANCING_METHOD, NORMALIZATION_METHOD, FEATURE_SELECTION_METHOD, MACHINE_LEARNING_MODEL

# Constants -------------------------------------------------------------------
IN_PATH = 'data/diabetia.csv' if ORIGIN == 'diabetia' else 'data/diabetia-disc.csv'
FOLD_PATH = f"data/fold_selection-{DIAGNOSTIC}.json"
MODEL_PATH = f"data/model-{DIAGNOSTIC}-{TEST_FOLD}-{ORIGIN}-{BALANCING_METHOD}-{NORMALIZATION_METHOD}-{FEATURE_SELECTION_METHOD}-{MACHINE_LEARNING_MODEL}.pkl"

OUT_PATH = f"data/prediction-{DIAGNOSTIC}-{TEST_FOLD}-{ORIGIN}-{BALANCING_METHOD}-{NORMALIZATION_METHOD}-{FEATURE_SELECTION_METHOD}-{MACHINE_LEARNING_MODEL}.csv"

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
df = df[df["id"].isin(ids)]

# normalize the data

# feature selection
logging.warning(f"features selection still not implemented, using all features")
features = df.columns.tolist()
features.remove("id")
features.remove(DIAGNOSTIC)

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
