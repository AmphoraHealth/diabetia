""" fold_selection.py
    creates a json file containing the data indices for each fold.
    each fold contains 20% of the data

    - The sampling is stratified by the target variable in addition to the
      - age bins (not implemented yet)
      - sex
      - hipertension
      - diabetes
    - The random seed is set to 42.

Input:
  - data/diabetia.csv
Output:
  - data/fold_selection-{diagnostic}.json
Additional outputs:
  - None
"""

# get complication from command line ------------------------------------------
import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from conf.global_constants import AUX_ORIGIN_DATABASE, S00_FOLD_SPLITING, DIAGNOSTIC
from libs.logging import logging

# Constants -------------------------------------------------------------------
IN_PATH = f"{AUX_ORIGIN_DATABASE}"
OUT_PATH = f"{S00_FOLD_SPLITING}.json"

COL_SEX = "cs_sex"
COL_HTN = "essential_(primary)_hypertension"
COL_DM = "diabetes_mellitus_type_2"

FOLDS = 5

# Import libraries ------------------------------------------------------------
import pandas as pd
import numpy as np
import json

np.random.seed(42)

# Code: fold selection --------------------------------------------------------
# general code to make stratified folds given the selected diagnostic
logging.info(f"making folds for {DIAGNOSTIC}")

# Load data 
df = pd.read_csv(IN_PATH)
df = df[[ "id", COL_SEX, COL_HTN, COL_DM, DIAGNOSTIC]]

# make a combined column to stratify by
df["_class"] = df[DIAGNOSTIC].astype(str)+"-"+df[COL_SEX].astype(str)
df = df[["id","_class"]]

# change class names to numbers
df["_code"] = df["_class"].astype("category").cat.codes

# create a mapping from class names to numbers
class_mapping = df[["_class","_code"]].drop_duplicates().set_index("_class").to_dict()["_code"]

# add a new column with random numbers and fixed seed
df["random"] = np.random.uniform(size=len(df))
# sort by _class and random
df = df.sort_values(by=["_class","random"])
df = df.reset_index(drop=True)

# print basic statistics by _class
print(df.groupby("_code").agg({"_class":"first","id":"count"}))

# make the folds using modulo {FOLDS}
folds = {i:{
  "ids": df.loc[df.index % FOLDS == i,"id"].tolist(),
  "cls": df.loc[df.index % FOLDS == i,"_code"].tolist()
  } for i in range(FOLDS)}

# add the class mapping to the folds dictionary
folds["class_mapping"] = class_mapping

# check directory existence and save the folds
if not os.path.exists(os.path.dirname(OUT_PATH)):
  os.makedirs(os.path.dirname(OUT_PATH))
with open(OUT_PATH,"w") as f:
  json.dump(folds,f,indent=2)

logging.info(f"folds saved to {OUT_PATH}")