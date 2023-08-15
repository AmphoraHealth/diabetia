""" 07_global_score.py
    This file contains the code for the global score.
    The averaged scores are:
      - balanced accuracy
      - f1 score

Input:
  - all scores by fold
Output:
  - data/global_score-{DIAGNOSTIC}-{ORIGIN}-{BALANCING_METHOD}-{NORMALIZATION_METHOD}-{FEATURE_SELECTION_METHOD}-{MACHINE_LEARNING_MODEL}.csv
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
IN_PATHS = [f"{S06_SCORE_BY_FOLD.replace('-{TEST_FOLD}-', str(i))}.csv" for i in range(len(FOLDS))]
OUT_PATH = f"{S07_GLOBAL_SCORE}.csv"
CODE_NAME = "-".join(S07_GLOBAL_SCORE.split("-")[1:])

# Import libraries ------------------------------------------------------------
import pandas as pd

# Code: global score ----------------------------------------------------------
# general code for global score given the selected diagnostic, origin, balancing_method, normalization_method, feature_selection_method and machine_learning_model

# Load data
dfs = {i: pd.read_csv(IN_PATH) for i, IN_PATH in enumerate(IN_PATHS)}

# Join the dataframes
df = pd.concat(dfs.values(), ignore_index=True)

# Get average of the scores
d = {"code": CODE_NAME}
for col in [c for c in df.columns if c != "fold"]:
  d[col] = df[col].mean()

# save the data
logging.info(f"saving global score to {OUT_PATH}")
df = pd.DataFrame(d, index=[0])
df.to_csv(OUT_PATH, index=False)
