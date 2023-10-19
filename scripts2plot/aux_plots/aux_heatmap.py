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
OUT_PATH = './data/supplementary_material/visualizations/'


# Import libraries
import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns


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
            columns:dict[str:str],
            groups:list[str],
            categories:dict[float:str]
        ):
        super().__init__(data = data, columns = columns, groups = groups)
        self.categories = categories

    def create_plot(self):
        """
        This function will generate n plots by "group_name". If the input only consider
        one group, loop process will run only once.
        """
        try:
            #..Create global dataframe
            tbl = self.fit_transform()

            #..loop through groups
            for group in list(tbl['group_name'].unique()):
                self._create_plot(
                    tbl=tbl,
                    group_name=group
                )

        except Exception as e:
            raise logging.error(f'{self.create_plot.__name__} failed. {e}')


    def _create_plot(
            self,
            tbl:pd.DataFrame,
            group_name:str
        ):
        """
        Function to make a heatmap
        """
        try:
            #..filter data and rename concept_names
            tbl = tbl.loc[tbl['group_name']==group_name].copy()
            tbl.loc[:,'concept_name'] = tbl['concept_name'].replace(to_replace=self.columns)

            #.. data preprocessing
            tbl['concept_name'] = tbl['concept_name'].replace(to_replace=self.columns)
            tbl = pd.pivot(tbl, index = 'concept_name', columns = 'categories', values = 'm')
            tbl = tbl[list(self.categories.values())]

            #..palette
            palette = sns.diverging_palette(220, 20, as_cmap=True)

            #..make plot
            plt.figure(figsize=(10,5))
            sns.heatmap(
                tbl, 
                annot = True, 
                cmap = palette,
                fmt = '.2f',
                center = 0,
                vmin = -5,
                vmax = 5
                )
            plt.ylabel('')
            plt.xlabel('')
            plt.title(f'{group_name.upper()} - slopes', fontsize = 14, y=1.01)
            plt.tight_layout()
            plt.savefig(OUT_PATH+'slope_heatmap_'+group_name+'.png', dpi = 300)

            return logging.info(f'{group_name} heatmap saved')
        
        except Exception as e:
            raise logging.error(f'{self.create_plot.__name__} failed. {e}')