""" merge_07_global_score.py
    This file contains the code for merging the global scores (by diagnostic) into a single file.
"""


# prepare environment ---------------------------------------------------------
# get constants from command line
import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.global_constants import *
from libs.logging import logging

# Import libraries ------------------------------------------------------------
import pandas as pd
from glob import glob

# Constants -------------------------------------------------------------------
IN_PATHS = glob(f"data/ml_data/07_global_score-x-{DIAGNOSTIC}-*.csv")
OUT_PATH = f"data/ml_data/merged_07_global_score-x-{DIAGNOSTIC}.csv"

# Code: merge -----------------------------------------------------------------
logging.info(f"{'='*30} merge started")

# load the data
files = [pd.read_csv(IN_PATH) for IN_PATH in IN_PATHS]

# merge the data
df = pd.concat(files, ignore_index=True)

# sort the data by balanced accuracy, f1 score, and roc auc score
df.sort_values(by=["balanced_accuracy", "f1", "roc"], ascending=False, inplace=True)

# save the data
df.to_csv(OUT_PATH, index=False)

# final message
logging.info(f"{'='*30} merge finished")