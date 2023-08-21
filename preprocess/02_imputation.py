""" 
imputation.py
    This file contains the functions for data imputation.

Input:
  - data/hk_database_cleaned.csv
Output:
  - data/diabetia.csv
Additional outputs:
  - None
"""

# get complication from command line ------------------------------------------
import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.logging import logging

# Constants
IN_PATH = 'data/hk_database_cleaned.csv'
OUT_PATH = 'data/diabetia.csv'
CONFIG_PATH = 'conf/columnGroups.json'

# Import libraries
import pandas as pd
import numpy as np
import json
import re
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

#..Default configurations
important_variables = ['cs_sex','age_at_wx', 'diabetes_mellitus_type_2', 'essential_(primary)_hypertension']
definitions = json.load(open(f'{CONFIG_PATH}', 'r', encoding='UTF-8'))

def validate(columns:list) -> list:
    valid_columns = []
    for c in columns:
        if c in definitions['diagnosisCols'] or c in definitions['drugsCols'] or c == "dx_age_e11":
            logging.warning(f'Invalid column to impute: "{c}"')
        else:
            valid_columns.append(c)

    #..drop label cols from categoricalCols group
    valid_columns = [col for col in valid_columns if bool(re.match('^.*_label$',str(col)))==False]
    return valid_columns

def fill_with_zero(data:pd.DataFrame, columns:list) -> pd.DataFrame:
    """
    Function to fill missing values with zero
    """
    for c in columns:
        data[c].fillna(0, inplace = True)
    return data

def impute_with_subset(data:pd.DataFrame, columns:list, subset:list = important_variables) -> pd.DataFrame:
    """
    Function to fill missing values using information from a subset of the variables in a DataFrame
    """
    imputed_dfs = []
    for c in columns:
        imp = IterativeImputer(initial_strategy = "mean", max_iter = 10, verbose = 0, random_state=0)
        subset_df = data[subset + [c]]
        imputed_subset = imp.fit_transform(subset_df)
        imputed_df = pd.DataFrame(imputed_subset, columns=subset_df.columns)
        data[c] = list(imputed_df[c])

    return data
    

def imputation(data:pd.DataFrame) -> pd.DataFrame:
    """
    Function to fill missing values
    """
    #..identify % null by col
    missing = data.isna().sum() / len(data)
    
    #..not consider categorical data to imputation
    missing = missing[[col for col in missing.index if bool(re.match('^.*_label',str(col)))==False and col!='dx_age_e11_cat']]

    cols_to_impute = list(missing[(missing<=0.3) & (missing>0)].index)
    cols_to_zero = list(missing[missing>0.3].index)

    cols_to_impute = validate(cols_to_impute)
    # cols_to_zero = validate(cols_to_zero)

    data = fill_with_zero(data, cols_to_zero)
    data = impute_with_subset(data, cols_to_impute)

    return data

def main():
    logging.info('Reading data...')
    data = pd.read_csv(f'{IN_PATH}')
    logging.info('Imputation process started')
    imputed_data = imputation(data)
    logging.info('Imputation process finished')
    imputed_data.to_csv(f'{OUT_PATH}', index = False)
    logging.info(f'Imputed data saved on {OUT_PATH}')

if __name__ == '__main__':
    main()
