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
from conf.global_constants import DIAGNOSTIC, TEST_FOLD, MODEL, SELECTION_METHOD

# Constants -------------------------------------------------------------------
OUT_PATH = f"data/prediction-{DIAGNOSTIC}-{TEST_FOLD}-{SELECTION_METHOD}-{MODEL}.csv"

DB_PATH = 'data/diabetia.csv'
FOLD_PATH = f"data/fold_selection-{DIAGNOSTIC}.json"
FEATURES_PATH = f"data/features_selected-{DIAGNOSTIC}-{TEST_FOLD}-{SELECTION_METHOD}.json"
MODEL_PATH = f"data/model-{DIAGNOSTIC}-{TEST_FOLD}-{SELECTION_METHOD}-{MODEL}.pkl"

# Import libraries ------------------------------------------------------------

# Code: prediction ------------------------------------------------------------
# general code for prediction on the test fold
#   taking into account the selected diagnostic, test_fold, selection_method and model
