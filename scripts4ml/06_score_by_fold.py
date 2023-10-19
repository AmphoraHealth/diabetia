""" 06_score_by_fold.py
    This file contains the code for scoring the model on the test fold.
    The metrics to implement are:
      - balanced accuracy
      - f1 score
      - auc (not implemented yet)

Input:
  - data/prediction-{DIAGNOSTIC}-{ORIGIN}-{TEST_FOLD}-{BALANCING_METHOD}-{NORMALIZATION_METHOD}-{FEATURE_SELECTION_METHOD}-{MACHINE_LEARNING_MODEL}.csv
Output:
  - data/score-{DIAGNOSTIC}-{ORIGIN}-{TEST_FOLD}-{BALANCING_METHOD}-{NORMALIZATION_METHOD}-{FEATURE_SELECTION_METHOD}-{MACHINE_LEARNING_MODEL}.json
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
IN_PATH = f"{S05_PREDICTION}.parquet"
OUT_PATH = f"{S06_SCORE_BY_FOLD}.csv"

# Import libraries ------------------------------------------------------------
from scipy.stats import bootstrap, pearsonr
from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score, recall_score, brier_score_loss
from aux_00_common import load_data
import pandas as pd

# Code: score -----------------------------------------------------------------
# general code for scoring the model on the test fold

# Load data
df = load_data(IN_PATH)

# make a confusion matrix of this data
confusion_matrix = pd.crosstab(df["real"], df["pred"], rownames=["real"], colnames=["pred"])
confusion_matrix = confusion_matrix.to_string()
confusion_matrix = "\n".join(["\t"+line for line in confusion_matrix.split("\n")])
logging.info(f"confusion matrix before:\n{confusion_matrix}")

# get only the rows where real is not 2.0
df = df.loc[df["real"] != 2.0]

# when predicted data is 2.0, change it to 1.0
df.loc[df["pred"] == 2.0, "pred"] = 1.0

# make a confusion matrix of the final data
confusion_matrix = pd.crosstab(df["real"], df["pred"], rownames=["real"], colnames=["pred"])
confusion_matrix = confusion_matrix.to_string()
confusion_matrix = "\n".join(["\t"+line for line in confusion_matrix.split("\n")])
logging.info(f"confusion matrix after:\n{confusion_matrix}")

# calculate the metrics
logging.info(f"calculating metrics")
balanced_accuracy = balanced_accuracy_score(df["real"], df["pred"])
f1 = f1_score(df["real"], df["pred"],pos_label=1)
roc = roc_auc_score(df["real"], df["pred"])
recall = recall_score(df["real"], df["pred"],pos_label=1)
bss = brier_score_loss(df["real"], df["pred"])

# save and print the metrics
logging.info(f"""
\tbalanced accuracy: {balanced_accuracy}
\tf1 score:          {f1}
\tbss:               {bss}
\tsaving score to    {OUT_PATH}""")
df = pd.DataFrame({"fold": TEST_FOLD, "balanced_accuracy": [balanced_accuracy], "f1": [f1], "roc": [roc], "recall": [recall], "bss": [bss]})
df.to_csv(OUT_PATH, index=False)

# final message
logging.info(f"{'='*30} scoring finished")
