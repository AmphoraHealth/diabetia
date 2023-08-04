""" model_train.py
    This file contains the code for the model training.

Input:
  - data/diabetia.csv
  - data/fold_selection-{complication}.json
  - data/features_selected-{complication}-{test_fold}.json
Output:
  - data/model-{complication}-{test_fold}.pkl
Additional outputs:
  - None
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
import os
import sys

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from conf.global_constants import *
from libs.logging import logging

# Constants -------------------------------------------------------------------
IN_PATH = f"data/balanced-{DIAGNOSTIC}-{TEST_FOLD}-{ORIGIN}-{BALANCING_METHOD}.csv"
FEATURES_PATH = f"data/features-{DIAGNOSTIC}-{TEST_FOLD}-{ORIGIN}-{BALANCING_METHOD}-{NORMALIZATION_METHOD}-{FEATURE_SELECTION_METHOD}.json"

OUT_PATH = f"data/model-{DIAGNOSTIC}-{TEST_FOLD}-{ORIGIN}-{BALANCING_METHOD}-{NORMALIZATION_METHOD}-{FEATURE_SELECTION_METHOD}-{MACHINE_LEARNING_MODEL}.pkl"

# Import libraries ------------------------------------------------------------
import pickle

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score

# Code: model training --------------------------------------------------------
# general code for model training given the selected machine learning model
#   taking into account the selected selection_method, diagnostic and test_fold

# Load data
df = pd.read_csv(IN_PATH)
logging.warning(f"features selection still not implemented, using all features")
features = df.columns.tolist()
features.remove("id")
features.remove(DIAGNOSTIC)
features.remove("age_diag_cat")

# select the model
m = {
  "logistic": LogisticRegression()
}[MACHINE_LEARNING_MODEL]

# train the model
logging.info(f"training model {MACHINE_LEARNING_MODEL}")
m.fit(df[features], df[DIAGNOSTIC])

# print the model balanced accuracy
logging.info(f"model train accuracy: {balanced_accuracy_score(df[DIAGNOSTIC], m.predict(df[features]))}")

# save the model
logging.info(f"saving model to {OUT_PATH}")
with open(OUT_PATH, "wb") as f:
    pickle.dump(m, f)
logging.info(f"model saved to {OUT_PATH}")