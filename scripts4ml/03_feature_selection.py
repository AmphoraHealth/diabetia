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
from libs.global_constants import *
from libs.logging import logging


# Constants -------------------------------------------------------------------
OUT_PATH = f"{S03_FEATURE_SELECTION}.json"
DB_PATH = f"{S02B_STANDARDIZATION}.csv"
FOLD_PATH = f"{S00_FOLD_SPLITING}.json"
CONFIG_PATH = './conf/engineering_conf.json'
definitions = json.load(open(f'{CONFIG_PATH}', 'r', encoding='UTF-8'))['config']['diagnosis']

# Import libraries ------------------------------------------------------------
from aux_03_feature_selection import methods
import pandas as pd
import json
# from sklearn.feature_selection import chi2
# from sklearn.naive_bayes import GaussianNB
# from sklearn.feature_selection import SequentialFeatureSelector

# Code: feature selection -----------------------------------------------------
# general code for feature selection given the selected FEATURE_SELECTION_METHOD
#   taking into account the selected diagnostic and test_fold
 
def get_fold_trainning(data:pd.DataFrame, folds_file:json, n_folds:int = 5) -> pd.DataFrame:
    train = []
    for n in range(n_folds):
        if str(n) == TEST_FOLD:
            pass
        else:
            # train.append(data.loc[data['id'].isin(folds_file[str(n)]['ids'])])
            train.append(data.loc[folds_file[str(n)]['ids']])
    train = pd.concat(train)
    return train

def feature_selection(data:pd.DataFrame, label:pd.Series, n_features:int) -> json:
    return methods[FEATURE_SELECTION_METHOD].fit(data, label, n_features)



def main():
    logging.info('Reading data...')
    data = pd.read_csv(f'{DB_PATH}', index_col = 0, low_memory=False)
    data.drop('e11', axis = 1, inplace = True)
    data.drop('dx_age_e11_cat', axis = 1, inplace = True)
    columns_to_drop = [x for x in data.columns if 'label' in x]
    data.drop(columns_to_drop, axis = 1, inplace = True)
    X, y = data.iloc[:,:-4], data[DIAGNOSTIC]
    logging.info(f"Starting feature selection process for {definitions[DIAGNOSTIC].replace('type_2_diabetes_mellitus', 'DM2').replace('_',' ')} using {FEATURE_SELECTION_METHOD} approach")
    features = feature_selection(X, y, n_features=100)

    with open(f'{OUT_PATH}', "w") as json_file:
        json.dump(features, json_file)


if __name__ == '__main__':
    main()