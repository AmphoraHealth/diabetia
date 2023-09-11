"""
aux_lineplot.py
This file contains the main function to create a database with slopes by variable. All numerical variables 
are considering for heatmap but to slope plot only a slice of them are consider. 

Input:
  - data/diabetia.csv
  - object from DatabaseConstructor
Output:
  - diabetia_lineplot.png
"""

# Constants
OUT_PATH = './data/visualizations/diabetia_lineplot.png'

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

class MakeLineplot(SlopeDatabaseConstructor):

    def __init__(
            self,
            data:pd.DataFrame,
            columns:dict[str:str]
        ):
        super().__init__(data = data, columns = columns)
    

    def create_plot(self, y_limits:dict=None):
        """
        Function to make a line slope plot
        """
        try:
            #..default vars
            age_labels:list[str] = {
                key:index for index, key in enumerate(self.config['ageAtWxConfig']['categories'].keys())
            }
            age_order:list = list(age_labels.keys())
            measureCols:list[str] = list(self.columns.keys())

            #..filter data and rename concept_names
            tbl = self.fit_transform()
            tbl['concept_name'] = tbl['concept_name'].replace(to_replace=self.columns)

            #....melt data
            aux_1 = pd.melt(tbl,id_vars = ['concept_name','age_at_wx_label'], value_vars = tbl.columns[2:-2])
            aux_2 = tbl.drop(columns=tbl.columns[3:-2])

            aux = pd.merge(aux_1,aux_2, on = ['concept_name','age_at_wx_label'], how='left')
            aux.dropna(subset='value',inplace=True)

            #....extra cols
            aux['y_predicted'] = aux.apply(lambda x: x['variable']*x['m'] + x['b'], axis=1)
            aux['variable'] = aux['variable'].astype(float)

            #..make plot
            figure = sns.lmplot(
                data = aux,
                x='variable',
                y='value',
                row = 'concept_name',
                hue = 'age_at_wx_label',
                palette= 'rocket_r',
                ci = None,
                height = 2,
                aspect = 2,
                facet_kws = {
                    'sharey':'row',
                    'sharex':True
                }
            )
            #..figure adjust
            figure.fig.subplots_adjust(hspace=0.5, top=1)
            figure.set_titles(
                template = '{row_name}',
                fontdict = {'fontsize':6}
                )
            figure.set_xlabels('Window')
            figure.set_ylabels('')
            figure.tight_layout()
            #figure._legend.remove()

            #....configure x axes
            for ax in figure.axes.flat:
                ax.set_xticks(np.arange(1,len(aux['variable'].unique())+1,1))

            #..add slope coeficients
            coefs = aux.groupby(['concept_name','age_at_wx_label'])['m'].max().reset_index()
            coefs_dict = {}
            for index, row in coefs.iterrows():
                concept_name = row['concept_name']
                age_at_wx_label = row['age_at_wx_label']
                m = row['m']
                if concept_name not in coefs_dict:
                    coefs_dict[concept_name] = {}
                coefs_dict[concept_name][age_at_wx_label] = m
           
            for ax, coef in zip(figure.axes.flat, coefs_dict.keys()):
                group_1 = coefs_dict[coef]['18-44']
                group_2 = coefs_dict[coef]['45-64']
                group_3 = coefs_dict[coef]['65>']
                
                ax.annotate(
                    f"Slopes:\n18-44:{group_1:.2f} | 45-64:{group_2:.2f} | 65>:{group_3:.2f}",
                    xy=(0.05, 0.95),
                    xycoords = 'axes fraction',
                    fontsize = 8
                )
            
            #..declare 'y' limits for each row
            if y_limits != None:
                if all([measure in figure.row_names for measure in y_limits.keys()]):
                    for i, row_name in enumerate(figure.row_names):
                        ax = figure.axes[i, 0]
                        ax.set_ylim(y_limits[row_name])
                else:
                    logging.warning('_y_limits did not match with input values.')

            #..save fig
            figure.savefig(OUT_PATH,dpi=300)

            return logging.info('Lineplot saved')
        
        except Exception as e:
            raise logging.error(f'{self.create_plot.__name__} failed. {e}')