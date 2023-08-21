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
import pandas as pd
import json
from sklearn.feature_selection import chi2
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_selection import SequentialFeatureSelector

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

def xi2_feature_selection(data:pd.DataFrame, label:pd.Series, n_features:int = 100) -> dict:
    # get a list of columns with negative values
    cols = [col for col in data.columns if data[col].min() < 0]
    # add the minimum value to each column to make them all positive
    data[cols] = data[cols] + abs(data[cols].min())
    # get the best features
    best_features = {}
    chi, p_vals = chi2(data, label)
    statistics = pd.DataFrame(zip(data.columns, chi, p_vals), columns = ['id', 'chi2', 'p-val']).sort_values('p-val')
    statistics = statistics.head(n_features)
    best_features['columns'] = list(statistics['id'])
    best_features['chi2'] = list(statistics['chi2'])
    best_features['p_val'] = list(statistics['p-val'])
    return best_features

def probabilistic_feature_selection(data:pd.DataFrame, label:pd.Series, n_features:int = 100):
    best_features = {}
    naive_bayes = GaussianNB()
    forward_selection = SequentialFeatureSelector(naive_bayes, n_features_to_select=n_features, direction="forward")
    forward_selection.fit(data, label)
    best_features['columns'] = list(data.columns[forward_selection.get_support()])
    
    return best_features

def dummy_feature_selection(data:pd.DataFrame, label:pd.Series):
    best_features = {}
    best_features['columns'] = list(data.columns)

    return best_features

def main():
    logging.info('Reading data...')
    data = pd.read_csv(f'{DB_PATH}', index_col = 0)
    data.drop('e11', axis = 1, inplace = True)
    folds = json.load(open(f'{FOLD_PATH}', 'r', encoding='UTF-8'))
    logging.info(f"Selecting fold {TEST_FOLD} as test and rest for feature selection")
    data = get_fold_trainning(data, folds)
    X, y = data.iloc[:,:-4], data[DIAGNOSTIC]
    logging.info(f"Starting feature selection process for {definitions[DIAGNOSTIC].replace('type_2_diabetes_mellitus', 'DM2').replace('_',' ')} using {FEATURE_SELECTION_METHOD} approach")
    if FEATURE_SELECTION_METHOD == 'xi2':
        features = xi2_feature_selection(X, y)
    elif FEATURE_SELECTION_METHOD == 'probabilistic':
        features = probabilistic_feature_selection(X, y, n_features = 3)
    elif FEATURE_SELECTION_METHOD == 'dummy':
        features = dummy_feature_selection(X, y)

    with open(f'{OUT_PATH}', "w") as json_file:
        json.dump(features, json_file)


if __name__ == '__main__':
    main()