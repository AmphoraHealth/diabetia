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
IN_PATHS = [f"{S06_SCORE_BY_FOLD.replace('-'+TEST_FOLD+'-', '-'+tf+'-')}.csv" for tf in FOLDS]
OUT_PATH = f"{S07_GLOBAL_SCORE}.csv"
CODE_NAME = "-".join(S07_GLOBAL_SCORE.split("-")[1:])

PRED_PATH = [ ip.replace("06_score", "05_prediction").replace(".csv",".parquet") for ip in IN_PATHS ]
PRED_OUT = OUT_PATH.replace(".csv", "_merged.csv")

# Import libraries ------------------------------------------------------------
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss
from scipy.stats import bootstrap

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

# code to merge the predictions by fold ---------------------------------------
logging.info(f"merging predictions")

# Load data
dfs2 = {i: pd.read_parquet(IN_PATH) for i, IN_PATH in enumerate(PRED_PATH)}

# Join the dataframes
dfp = pd.concat(dfs2.values(), ignore_index=True)

# remove id column
dfp = dfp.drop(columns=["id"])

# rename and reorder columns
dfp = dfp.rename(columns={"real": "actual", "pred": "predicted"})

# remove rows where actual is 2.0
dfp = dfp.loc[dfp["actual"] != 2.0]

# update the merged prediction metrics ----------------------------------------
logging.info(f"updating merged predictions metrics")

# if roc is in the columns, calculate it
if "roc" in df.columns:
  roc = roc_auc_score(dfp["actual"], dfp["predicted"])
  logging.info(f"roc auc score calculated (old/new): {d['roc']}/{roc}")
  d["roc"] = roc

# if bss is in the columns, calculate it
if "bss" in df.columns:
  bss = brier_score_loss(dfp["actual"], dfp["predicted"])
  logging.info(f"brier score loss calculated (old/new): {d['bss']}/{bss}")
  d["bss"] = bss

# save the data ---------------------------------------------------------------

# save the data
logging.info(f"saving global score to {OUT_PATH}")
df = pd.DataFrame(d, index=[0])
df.to_csv(OUT_PATH, index=False)

# save the merged predictions
logging.info(f"saving merged predictions to {PRED_OUT}")
dfp.to_csv(PRED_OUT, index=False)
