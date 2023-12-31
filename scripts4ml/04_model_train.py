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
from libs.global_constants import *
from libs.logging import logging

# Constants -------------------------------------------------------------------
IN_PATH = f"{S02B_STANDARDIZATION}.parquet"
FEATURES_PATH = f"{S03_FEATURE_SELECTION}.json"

OUT_PATH = f"{S04_MODEL_TRAIN}.pkl"

# Import libraries ------------------------------------------------------------
import pickle

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score
from aux_04_model_train import models
from aux_00_common import *

# Code: model training --------------------------------------------------------
# general code for model training given the selected machine learning model
#   taking into account the selected selection_method, diagnostic and test_fold
logging.info(f"{'='*30} {MACHINE_LEARNING_MODEL} training started")

# Load data
df = load_data(IN_PATH)

# load features
features = load_data(FEATURES_PATH)["columns"]

# change diagnostic from 2.0 to 1.0
df.loc[df[DIAGNOSTIC] == 2.0, DIAGNOSTIC] = 1.0

# select the model
m = models[MACHINE_LEARNING_MODEL]

# train the model
logging.info(f"training model {MACHINE_LEARNING_MODEL}")
m.fit(df[features], df[DIAGNOSTIC])

# print the model balanced accuracy
logging.info(f"model train accuracy: {balanced_accuracy_score(df[DIAGNOSTIC], m.predict(df[features]))}")

# save the model
logging.info(f"saving model to {OUT_PATH}")
save_data(m, OUT_PATH)
logging.info(f"model saved to {OUT_PATH}")

# final message
logging.info(f"{'='*30} {MACHINE_LEARNING_MODEL} training finished")