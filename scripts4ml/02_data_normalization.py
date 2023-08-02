"""
INPUT: 
    - csv file
OUTPUT: 
    - csv file
    - pickle transformers
        - normalization
        - standardization
"""

""" feature_selection.py
    This file contains the code for feature selection.
    The list of features to be selected is stored in a json file.

Input:
  - data/hk_database_balanced.csv
Output:
  - data/hk_database_normalized.csv
Additional outputs:
  - Pickle file
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
from conf.global_constants import NORMALIZATION_METHODS 

# Constants -------------------------------------------------------------------
OUT_PATH = f"data/features_selected-{DIAGNOSTIC}-{TEST_FOLD}-{SELECTION_METHOD}.json"

DB_PATH = 'data/diabetia.csv'
FOLD_PATH = f"data/fold_selection-{DIAGNOSTIC}.json"

# Import libraries ------------------------------------------------------------

# Code: feature selection -----------------------------------------------------
# general code for feature selection given the selected selection_method
#   taking into account the selected diagnostic and test_fold
