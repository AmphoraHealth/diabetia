"""
aux_heatmap.py
This file contains the main function to create a database with slopes by variable. All numerical variables 
are considering for heatmap but to slope plot only a slice of them are consider. 

Input:
  - data/diabetia.csv
  - object from DatabaseConstructor
Output:
  - diabetia_heatmap.png
"""

# Constants
OUT_PATH = './data/visualizations/diabetia_heatmap.png'


# Import libraries
import pandas as pd
import numpy as np
import re
import os
import json
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from alive_progress import alive_bar


ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir
    )
)

sys.path.append(ROOT_PATH)
from libs.logging import logging
from scripts2plot.aux_plots.aux_slope_matrix import SlopeDatabaseConstructor


class MakeHeatmap(SlopeDatabaseConstructor):
    
    def __init__(
            self,
            data:pd.DataFrame,
            columns:dict[str:str]
        ):
        super().__init__(data = data, columns = columns)


    def create_plot(self):
        """
        Function to make a heatmap
        """
        try:
            #..default var
            age_labels:list[str] = {
                key:index for index, key in enumerate(self.config['ageAtWxConfig']['categories'].keys())
            }
            age_order:list = list(age_labels.keys())

            #.. data preprocessing
            tbl = self.fit_transform()
            tbl['concept_name'] = tbl['concept_name'].replace(to_replace=self.columns)
            tbl = pd.pivot(tbl, index = 'concept_name', columns = 'age_at_wx_label', values = 'm')
            tbl = tbl[age_order]

            #..make plot
            plt.figure(figsize=(10,5))
            sns.heatmap(
                tbl, 
                annot=True, 
                cmap='vlag',
                fmt = '.2f',
                center = 0,
                vmin = -5,
                vmax = 5
                )
            plt.ylabel('')
            plt.xlabel('Age group', fontsize = 8)
            plt.title('Slopes by window (1-14)', fontsize = 14, y=1.01)
            plt.tight_layout()
            plt.savefig(OUT_PATH, dpi = 300)

            return logging.info('Heatmap saved')
        
        except Exception as e:
            raise logging.error(f'{self.create_plot.__name__} failed. {e}')