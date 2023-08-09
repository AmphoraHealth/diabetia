""" class_balancing.py
    This file contains the code for class balancing.
    The valid balancing methods are:
      - unbalanced
      - undersampling(not implemented yet)
      - oversampling (not implemented yet)
      - mixed (not implemented yet)

Input:
  - data/diabetia[-disc].csv
  - data/fold_selection-{DIAGNOSTIC}.json
Output:
  - data/balanced-{DIAGNOSTIC}-{ORIGIN}-{TEST_FOLD}.csv
Additional outputs:
  - None
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from conf.global_constants import ORIGIN, TEST_FOLD, BALANCING_METHOD, AUX_ORIGIN_DATABASE ,S00_FOLD_SPLITING, S01_BALANCING
import aux_01_class_balancing as aux

# Constants -------------------------------------------------------------------
IN_PATH = f"{AUX_ORIGIN_DATABASE}"
FOLD_PATH = f"{S00_FOLD_SPLITING}.json"

OUT_PATH = f"{S01_BALANCING}.csv"

# Import libraries ------------------------------------------------------------
import pandas as pd
import json

# Code: class balancing -------------------------------------------------------
# general code for class balancing given the selected diagnostic, origin and test_fold
#   taking into account the selected balancing_method

# Load data
df = pd.read_csv(IN_PATH)
with open(FOLD_PATH) as f:
  fold_selection = json.load(f)

# function to balance the data
f = {
  "unbalanced": aux.unbalanced,
  "undersampling": aux.undersampling,
  "oversampling": aux.oversampling,
  "mixed": aux.mixed
}

# balance the data
df = f[BALANCING_METHOD](df, fold_selection, TEST_FOLD)

# save the data
df.to_csv(OUT_PATH, index=False)
