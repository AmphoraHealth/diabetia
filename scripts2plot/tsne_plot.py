""" 
tsne_plot.py
    This file contains the functions to generate tsne plot

Input:
  - data/diabetia.csv
Output:
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
CONFIG_PATH = './conf/engineering_conf.json'
#DIAGNOSTIC = sys.argv[1]
DIAGNOSTIC = 'e112'
DIAGNOSTIC = DIAGNOSTIC.lower()
color_pallette = {
    'e112':{'No complication': '#95A5A6', 'De novo complication':'#E74C3C', 'Pre-existing complication':'#FFA07A'},
    'e113':{'No complication': '#95A5A6', 'De novo complication':'#3498DB', 'Pre-existing complication':'#ADD8E6'},
    'e114':{'No complication': '#95A5A6', 'De novo complication':'#2ECC71', 'Pre-existing complication':'#98FB98'},
    'e115':{'No complication': '#95A5A6', 'De novo complication':'#FF5733', 'Pre-existing complication':'#8B4513'}
}



#Libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import json

#Default config
warnings.filterwarnings("ignore")
definitions = json.load(open(f'{CONFIG_PATH}', 'r', encoding='UTF-8'))['config']['diagnosis']
variables_for_tsne = ['birthdate','cs_sex', 'diabetes_mellitus_type_2', 'essential_(primary)_hypertension', 'in_glucose_median', 'fn_fasting_glucose_median', 'fn_capillary_glucose_median', 'fn_left_foot_median', 'fn_right_foot_median', 'fn_hemoglobin_median', 'albumin', 'fn_cholesterol_median', 'fn_creatinine_median', 'glucose']

#Functions
def read_data(file:str) -> pd.DataFrame:
    """
    Function to read data
    """
    data = pd.read_csv(file, low_memory = True, index_col = 0)
    X_data = data.iloc[:, :-5]
    y_data = data.iloc[:, -5:]
    return X_data, y_data


def generate_tsne_plot(data:pd.DataFrame, label:pd.Series):
    data = data[variables_for_tsne]
    scaler = MinMaxScaler()
    data = pd.DataFrame(scaler.fit_transform(data), columns = data.columns)
    data['label'] = list(label)
    lab2 = data[data['label'] == 2]
    lab1 = data[data['label'] == 1]
    lab0 = data[data['label'] == 0]

    lab0 = lab0.sample(n=len(lab0)//3, replace = False)

    final = pd.concat([lab0, lab1, lab2])

    values_name = {0: 'No complication', 1:'De novo complication', 2:'Pre-existing complication'}
    final['label'] = final['label'].replace(values_name)

    label_final = list(final['label'])
    final.drop('label', axis = 1, inplace = True)
    logging.info('Applying t-SNE transformation...')
    X_embedded = TSNE(random_state = 0).fit_transform(final)
    logging.info('End t-SNE transformation...')
    X_embedded_df = pd.DataFrame(X_embedded, columns = ['x', 'y'])
    X_embedded_df['label'] = label_final

    plt.figure(figsize=(12, 12))
    plt.axis('off')
    plt.tight_layout()
    sns.scatterplot(X_embedded_df, x = 'x', y='y', hue = 'label', alpha = 0.6, palette= color_pallette[DIAGNOSTIC])
    sns.scatterplot(X_embedded_df[X_embedded_df['label'] == 'De novo complication'], x = 'x', y='y', color = color_pallette[DIAGNOSTIC]['De novo complication'], alpha = 0.9)
    plt.savefig(f'{OUT_PATH_IMG}/tsne_{DIAGNOSTIC}.png', dpi = 200)
    plt.show()

def main():
    logging.info('Reading data...')
    X_data, y_data = read_data(f'{IN_PATH}')
    generate_tsne_plot(X_data, y_data[DIAGNOSTIC])


if __name__ == "__main__":
    main()