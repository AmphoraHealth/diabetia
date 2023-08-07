""" feature_selection.py
    This file contains the code for feature selection.
    The list of features to be selected is stored in a json file.

Input:
  - data/diabetia.csv
  - data/fold_selection-{complication}.json
Output:
  - data/features_selected-{complication}-{test_fold}.json
Additional outputs:
  - None
"""

# prepare environment ---------------------------------------------------------
import os
import sys

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from conf.global_constants import *
from libs.logging import logging

# get constants from command line
from conf.global_constants import DIAGNOSTIC, TEST_FOLD, FEATURE_SELECTION_METHOD

# Constants -------------------------------------------------------------------
OUT_PATH = f"data/features_selected-{DIAGNOSTIC}-{TEST_FOLD}-{FEATURE_SELECTION_METHOD}.json"
DB_PATH = 'data/diabetia.csv'
FOLD_PATH = f"data/fold_selection-{DIAGNOSTIC}.json"

# Import libraries ------------------------------------------------------------
import pandas as pd
import json
from sklearn.feature_selection import chi2


# Code: feature selection -----------------------------------------------------
# general code for feature selection given the selected FEATURE_SELECTION_METHOD
#   taking into account the selected diagnostic and test_fold
 
def get_fold_trainning(data:pd.DataFrame, folds_file:json, n_folds:int = 5) -> pd.DataFrame:
    train = []
    for n in range(n_folds):
        if n == TEST_FOLD:
            pass
        else:
            train.append(data.loc[folds_file[str(n)]['ids']])
    train = pd.concat(train)
    return train

def feature_selection(data:pd.DataFrame, label:pd.Series, n_features:int = 100) -> dict:
    best_features = {}
    chi, p_vals = chi2(data, label)
    statistics = pd.DataFrame(zip(data.columns, chi, p_vals), columns = ['id', 'chi2', 'p-val']).sort_values('p-val')
    statistics = statistics.head(n_features)
    best_features['columns'] = list(statistics['id'])
    best_features['chi2'] = list(statistics['chi2'])
    best_features['p_val'] = list(statistics['p-val'])
    return best_features

def main():
    data = pd.read_csv(f'{DB_PATH}', index_col = 0)
    data.drop('e11', axis = 1, inplace = True)
    folds = json.load(open(f'{FOLD_PATH}', 'r', encoding='UTF-8'))
    data = get_fold_trainning(data, folds)
    X, y = data.iloc[:,:-4], data[DIAGNOSTIC]
    features = feature_selection(X, y)

    with open(f'{OUT_PATH}', "w") as json_file:
        json.dump(features, json_file)


if __name__ == '__main__':
    main()