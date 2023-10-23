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
DIAGNOSTIC = DIAGNOSTIC.lower()


#Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats.contingency import relative_risk
from scipy.stats.contingency import odds_ratio
import json
import warnings
import re

#Default config
warnings.filterwarnings("ignore")
complications = {'e112':'Renal complications', 'e113':'Ophthalmic complications', 'e114':'Neurological complications', 'e115':'Circulatory complications'}
definitions = json.load(open(f'{CONFIG_PATH}', 'r', encoding='UTF-8'))['config']['diagnosis']


#Functions
def read_data(file:str, all_ = True) -> pd.DataFrame:
    """
    Function to read data
    """
    data = pd.read_csv(file, low_memory = True, index_col = 0)
    if all_:
        X_data = data.iloc[:, :-5]
        y_data = data.iloc[:, -5:]
    else:
        data = data[data['diabetes_mellitus_type_2']==1]
        X_data = data.iloc[:, :-5]
        y_data = data.iloc[:, -5:]

    return X_data, y_data

def process_string(input_string: str) -> str:
    processed_string = re.sub(r'^(fn_|cs_|in_)', '', input_string)
    processed_string = processed_string.replace('_', ' ')
    processed_string = re.sub(r'\b(label|binary|ordinal)\b', '', processed_string)
    return processed_string

def get_binary_features(data:pd.DataFrame) -> pd.DataFrame:
    """
    Function to return a subset of binary variables from the dataset
    """
    data['years since T2D Dx = 0-4'] = [1 if x <= 4 else 0 for x in data['years_since_dx']]
    data['years since T2D Dx = 5-14'] = [1 if x >= 5 and x <= 14 else 0 for x in data['years_since_dx']]
    data['years since T2D Dx >= 15'] = [1 if x >= 15 else 0 for x in data['years_since_dx']]
    data['Sex = Female'] = [1 if x == 0 else 0 for x in data['cs_sex']]
    data['Sex = Male'] = list(data['cs_sex'])
    data['years at window = 18-44'] = [1 if x >= 18 and x <= 44 else 0 for x in data['age_at_wx']]
    data['years at window = 45-64'] = [1 if x >= 45 and x <= 64 else 0 for x in data['age_at_wx']]
    data['years at window >= 65'] = [1 if x >= 65 else 0 for x in data['age_at_wx']]
    data['years at T2D Dx = 18-44'] = [1 if x >= 18 and x <= 44 else 0 for x in data['dx_age_e11']]
    data['years at T2D Dx = 45-64'] = [1 if x >= 45 and x <= 64 else 0 for x in data['dx_age_e11']]
    data['years at T2D Dx >= 65'] = [1 if x >= 65 else 0 for x in data['dx_age_e11']]
    data['BMI = Overweight & Obesity'] = [1 if x >= 25 else 0 for x in data['bmi_value']]
    data['T2D (E11) = True'] = list(data['diabetes_mellitus_type_2'])
    data['Hypertension (I10) = True'] = list(data['essential_(primary)_hypertension'])
    data['Dyslipidemia (E78) = True'] = list(data['disorders_of_lipoprotein_metabolism_and_other_lipidemias'])
    data['eGFR = Low (female)'] = [1 if x < 60 and x !=0 and y == 0 else 0 for x,y in zip(data['gfr_value'], data['cs_sex'])] 
    data['eGFR = Low (male)'] = [1 if x < 60 and x !=0 and y == 1 else 0 for x,y in zip(data['gfr_value'], data['cs_sex'])]
    data['Glucose = High'] = [1 if x >= 126 else 0 for x in data['glucose_value']]
    data['HbA1c = High'] = [1 if x >= 6 else 0 for x in data['hemoglobin_value']]
    data['Triglycerides = High'] = [1 if x >= 150 else 0 for x in data['triglycerides_value']]
    data['cholesterol = High'] = [1 if x >= 200 else 0 for x in data['cholesterol_value']]

    complete_set = data.loc[:,'years since T2D Dx = 0-4':]
    # print([0 if x > 5 else 1 for x in data['years_since_dx']])

    return complete_set

def get_relative_risk(X_data:pd.DataFrame, y_data:pd.Series) -> pd.DataFrame:
    """
    Function to calculate relative risk by feature
    """
    variable, effect, lower_int, upper_int = [], [], [], []
    X_data['label'] = list(y_data)
    for c in X_data.columns[:-1]:
        try:
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
            variable.append(c)
        except:
            pass

    X_data.drop('label', axis = 1, inplace = True)
    rr_df = pd.DataFrame(zip(variable, effect, lower_int, upper_int), columns = ['Variable', 'RelativeRisk', 'Lower', 'Upper'])
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
    plt.xlabel(f'{effect}', fontsize=20)
    plt.ylabel('Variables', fontsize=20)
    plt.title(f'Forest Plot of {effect} for {complications[DIAGNOSTIC]}', fontsize=25)
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
    X_data, y_data = read_data(f'{IN_PATH}', all_ = True)
    X_data = get_binary_features(X_data)

    logging.info(f"Calculating Relative Risk of {definitions[DIAGNOSTIC].replace('type_2_diabetes_mellitus', 'DM2').replace('_',' ')} for {len(X_data.columns)} variables...")
    rr_df = get_relative_risk(X_data, y_data[DIAGNOSTIC])
    rr_df.to_csv(f'{OUT_PATH_DATA}/RelativeRisk_{DIAGNOSTIC}.csv', index = False)


    logging.info(f"Calculating Odds Ratio of {definitions[DIAGNOSTIC].replace('type_2_diabetes_mellitus', 'DM2').replace('_',' ')} for {len(X_data.columns)} variables...")
    or_df = get_odds_ratio(X_data, y_data[DIAGNOSTIC])
    or_df.to_csv(f'{OUT_PATH_DATA}/OddsRatio_{DIAGNOSTIC}.csv', index = False)

    logging.info('Generating forest plots...')
    forest_plot(rr_df[(rr_df['RelativeRisk'] > 0) & (rr_df['RelativeRisk'] < float('inf'))], 'Variable', 'RelativeRisk', 'Lower', 'Upper', f'RelativeRiskFp_{DIAGNOSTIC}', logscale = True, figsize = (21,38))
    forest_plot(or_df[(or_df['OddsRatio'] > 0) & (or_df['OddsRatio'] < float('inf'))], 'Variable', 'OddsRatio', 'Lower', 'Upper', f'OddsRatioFp_{DIAGNOSTIC}', logscale = True, figsize = (21,38))


if __name__ == "__main__":
    main()
        