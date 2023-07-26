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

# Constants
IN_PATH = 'data/hk_database_cleaned.csv'
OUT_PATH = 'data/diabetia.csv'

# Import libraries
import pandas as pd
import numpy as np
import logging
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

#..Default configurations
logging_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format, datefmt='%d-%m-%y %H:%M:%S')
important_variables = ['df_nacimiento','cs_sexo','age_at_wx', 'diabetes_mellitus_tipo_2', 'hipertension_esencial_(primaria)']

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

    missing = data.isna().sum() / len(data)

    cols_to_impute = list(missing[(missing<=0.3) & (missing>0)].index)
    cols_to_zero = list(missing[missing>0.3].index)
    # cols_complete = list(missing[missing == 0].index)

    data = fill_with_zero(data, cols_to_zero)
    data = impute_with_subset(data, cols_to_impute)

    return data

if __name__ == '__main__':
    logging.info('Reading data...')
    data = pd.read_csv(f'{IN_PATH}')
    logging.info('Imputation process started')
    imputed_data = imputation(data)
    logging.info('Imputation process finished')
    imputed_data.to_csv(f'{OUT_PATH}')
    logging.info(f'Imputed data saved on {OUT_PATH}')
