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
from conf.global_constants import DIAGNOSTIC, TEST_FOLD, MODEL, SELECTION_METHOD

# Constants -------------------------------------------------------------------
OUT_PATH = f"data/model-{DIAGNOSTIC}-{TEST_FOLD}-{SELECTION_METHOD}-{MODEL}.pkl"

DB_PATH = 'data/diabetia.csv'
FOLD_PATH = f"data/fold_selection-{DIAGNOSTIC}.json"
FEATURES_PATH = f"data/features_selected-{DIAGNOSTIC}-{TEST_FOLD}-{SELECTION_METHOD}.json"

# Import libraries ------------------------------------------------------------

# Code: model training --------------------------------------------------------
# general code for model training given the selected machine learning model
#   taking into account the selected selection_method, diagnostic and test_fold
