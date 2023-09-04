""" 
forest_plots.py
    This file contains the functions to generate forest plots

Input:
  - data/diabetia.csv
Output:
  - effects.csv(CHANGE)
Additional outputs:
  - forest_plots.png(CHANGE)
"""

# Environment preparation
import os
import sys

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.logging import logging


# Constant definition
IN_PATH = 'data/diabetia.csv'
OUT_PATH_IMG = 'data/supplementary_material/visualizations'
OUT_PATH_DATA = 'data/supplementary_material/data_aux'
CONFIG_PATH = './conf/engineering_conf.json'
DIAGNOSTIC = sys.argv[1]


#Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.contingency import relative_risk
from scipy.stats.contingency import odds_ratio
import json
import sys
import warnings

#Default config
warnings.filterwarnings("ignore")
definitions = json.load(open(f'{CONFIG_PATH}', 'r', encoding='UTF-8'))['config']['diagnosis']


#Functions
def read_data(file:str) -> pd.DataFrame:
    """
    Function to read data
    """
    data = pd.read_csv(file, low_memory = True, index_col = 0)
    X_data = data.iloc[:, :-5]
    y_data = data.iloc[:, -5:]
    return X_data, y_data

def get_binary_features(data:pd.DataFrame) -> pd.DataFrame:
    """
    Function to return a subset of binary variables from the dataset
    """
    binary_feats = []
    ordinal_feats = []
    for c in data.columns:
        if len(data[c].unique()) == 2:
            binary_feats.append(c)
        elif 'ordinal' in c:
            if c.replace('ordinal', 'label') in data.columns:
                ordinal_feats.append(c.replace('ordinal', 'label'))
            else: 
                data[c] = data[c].astype(int).astype(str)
                ordinal_feats.append(c)

    one_hot_variables = pd.get_dummies(data[ordinal_feats], drop_first = False)
    complete_set = pd.concat([data[binary_feats], one_hot_variables], axis = 1)
    complete_set.columns = [x.replace('_', ' ') for x in complete_set.columns]

    return complete_set

def get_relative_risk(X_data:pd.DataFrame, y_data:pd.Series) -> pd.DataFrame:
    """
    Function to calculate relative risk by feature
    """
    effect, lower_int, upper_int = [], [], []
    X_data['label'] = list(y_data)
    for c in X_data.columns[:-1]:
        controlled = X_data[X_data[c] == 0]
        controlled_total = len(controlled)
        controlled_cases = len(controlled[controlled['label'] == 1])
        
        experimental = X_data[X_data[c] == 1]
        experimental_total = len(experimental)
        experimental_cases = len(experimental[experimental['label'] == 1])

        rr = relative_risk(experimental_cases, experimental_total,controlled_cases, controlled_total)
        interval = rr.confidence_interval(confidence_level=0.95)

        effect.append(rr.relative_risk)
        lower_int.append(interval.low)
        upper_int.append(interval.high)

    X_data.drop('label', axis = 1, inplace = True)
    rr_df = pd.DataFrame(zip(X_data.columns[:-1], effect, lower_int, upper_int), columns = ['Variable', 'RelativeRisk', 'Lower', 'Upper'])
    return rr_df

def get_odds_ratio(X_data:pd.DataFrame, y_data:pd.Series) -> pd.DataFrame:
    """
    Function to calculate Odds Ratio by feature
    """
    effect, lower_int, upper_int = [], [], []
    X_data['label'] = list(y_data)
    for c in X_data.columns[:-1]:
        controlled = X_data[X_data[c] == 0]
        controlled_negative_cases = len(controlled[controlled['label'] == 0])
        controlled_positive_cases = len(controlled[controlled['label'] == 1])
        
        experimental = X_data[X_data[c] == 1]
        experimental_negative_cases = len(experimental[experimental['label'] == 0])
        experimental_positive_cases = len(experimental[experimental['label'] == 1])

        or_ = odds_ratio([[experimental_positive_cases, controlled_positive_cases], [experimental_negative_cases, controlled_negative_cases]])
        interval = or_.confidence_interval(confidence_level=0.95)

        effect.append(or_.statistic)
        lower_int.append(interval.low)
        upper_int.append(interval.high)

    X_data.drop('label', axis = 1, inplace = True)
    or_df = pd.DataFrame(zip(X_data.columns[:-1], effect, lower_int, upper_int), columns = ['Variable', 'OddsRatio', 'Lower', 'Upper'])
    return or_df

def forest_plot(df:pd.DataFrame, variables:str, effect:str, low:str, high:str, plot_name:str, reference_value:int = 1, ascending:bool = False, logscale:bool = False, figsize:tuple = (20,60)):
    """
    Function to generate a forest plot from an risk effect estimation
    """
    if ascending:
        df.sort_values(by = effect, ascending = False, inplace = True)
    else:
        df.sort_values(by = effect, ascending = True, inplace = True)

    x_err_low = [list(df[effect])[i] - list(df[low])[i] for i in range(len(df))]
    x_err_high = [list(df[high])[i] - list(df[effect])[i] for i in range(len(df))]


    plt.figure(figsize=figsize)

    plt.errorbar(list(df[effect]), np.arange(len(df)), xerr=[x_err_low, x_err_high], fmt='.', color='gray', capsize=5, label='Confidence Intervals', zorder=0)
    plt.scatter(list(df[effect]), np.arange(len(df)), color='black',marker='s', label='Relative Risk', zorder=10)
    plt.axvline(x=reference_value, color='red', linestyle='--', label='Reference', alpha = 0.6)

    plt.yticks(np.arange(len(df)), list(df[variables]))
    plt.xlabel(f'{effect}', fontsize=18)
    plt.ylabel('Variables', fontsize=18)
    plt.title(f'Forest Plot of {effect}', fontsize=20)
    plt.legend()
    plt.grid(axis='x', linestyle='--', alpha=0.8)
    plt.grid(axis='y', linestyle='--', alpha=0.8)
    if logscale == True:
        plt.xscale('log')
    plt.tick_params(axis='y', which='major', labelsize=10)
    plt.tick_params(axis='x', which='major', labelsize=12)
    plt.tight_layout()
    plt.savefig(f'{OUT_PATH_IMG}/{plot_name}.png', dpi = 300)   

def main():
    logging.info('Reading data...')
    X_data, y_data = read_data(f'{IN_PATH}')
    X_data = get_binary_features(X_data)

    logging.info(f"Calculating Relative Risk of {definitions[DIAGNOSTIC].replace('type_2_diabetes_mellitus', 'DM2').replace('_',' ')} for {len(X_data.columns)} variables...")
    rr_df = get_relative_risk(X_data, y_data[DIAGNOSTIC])
    rr_df.to_csv(f'{OUT_PATH_DATA}/RelativeRisk_{DIAGNOSTIC}.csv', index = False)


    logging.info(f"Calculating Odds Ratio of {definitions[DIAGNOSTIC].replace('type_2_diabetes_mellitus', 'DM2').replace('_',' ')} for {len(X_data.columns)} variables...")
    or_df = get_odds_ratio(X_data, y_data[DIAGNOSTIC])
    or_df.to_csv(f'{OUT_PATH_DATA}/OddsRatio_{DIAGNOSTIC}.csv', index = False)

    logging.info('Generating forest plots...')
    forest_plot(rr_df[rr_df['RelativeRisk'] > 0], 'Variable', 'RelativeRisk', 'Lower', 'Upper', f'RelativeRiskFp_{DIAGNOSTIC}', logscale = True, figsize = (21,27))
    forest_plot(or_df[or_df['OddsRatio'] > 0], 'Variable', 'OddsRatio', 'Lower', 'Upper', f'OddsRatioFp_{DIAGNOSTIC}', logscale = True, figsize = (21,27))


if __name__ == "__main__":
    main()