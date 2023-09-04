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
from libs.logging import logging
from libs.global_constants import *
import aux_01_class_balancing as aux
from aux_00_common import *

# Constants -------------------------------------------------------------------
IN_PATH = f"{AUX_ORIGIN_DATABASE}"
FOLD_PATH = f"{S00_FOLD_SPLITING}.json"

OUT_PATH = f"{S01_BALANCING}.parquet"

# Import libraries ------------------------------------------------------------
import pandas as pd
import json

# Code: class balancing -------------------------------------------------------
# general code for class balancing given the selected diagnostic, origin and test_fold
#   taking into account the selected balancing_method
logging.info(f"{'='*30} class balancing started")

# Load data
df = load_data(IN_PATH)
fold_selection = load_data(FOLD_PATH)

# get the list of valid ids not in the test fold
folds = [fold_selection[str(i)]["ids"] for i in range(5) if str(i) != TEST_FOLD]
ids = [item for sublist in folds for item in sublist]

# filter the data to get only rows where the id is in the list
df = df.loc[df["id"].isin(ids)]

# balance the data
df = aux.methods[BALANCING_METHOD](df, fold_selection, TEST_FOLD)

# save the data
save_data(df, OUT_PATH)

# final message
logging.info(f"{'='*30} class balancing finished")
