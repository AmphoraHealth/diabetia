"""
aux_lineplot.py
This file contains the main function to create a database with slopes by variable. All numerical variables 
are considering for heatmap but to slope plot only a slice of them are consider. 

Input:
  - data/diabetia.csv
  - object from DatabaseConstructor
Output:
  - diabetia_lineplot_n.png
    - By n grups detected
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

class MakeLineplot(SlopeDatabaseConstructor):

    def __init__(
            self,
            data:pd.DataFrame,
            columns:dict[str:str],
            groups:list[str],
            palette:dict[str:str]
        ):
        super().__init__(data = data, columns = columns, groups = groups)
        self.palette = palette

    
    def create_plot(
            self,
            y_limits:dict=None
            ):
        """
        This function will generate n plots by "group_name". If the input only consider 
        one group, loop process will run only once. It is required to give as an input a y_limits
        dictionary with personalized ranges for variables, if not, automatically yTicks will be
        created
        """
        try:
            #..Create global database
            tbl = self.fit_transform()
            
            #..loop through groups
            for group in list(tbl['group_name'].unique()):
                palette_colors:dict = self.palette[group]
                self._create_plot(
                    tbl=tbl, 
                    y_limits=y_limits, 
                    group_name=group, 
                    palette_colors = palette_colors 
                )
                
        except Exception as e:
            raise logging.error(f'{self.create_plot.__name__} failed. {e}')
            
    

    def _create_plot(
            self,
            tbl:pd.DataFrame, 
            y_limits:dict=None, 
            group_name:str = None,
            palette_colors:dict = None
            ):
        """
        Function to make a line slope plot
        """
        try:
            #..filter data and rename concept_names
            tbl = tbl.loc[tbl['group_name']==group_name].copy()
            tbl.loc[:,'concept_name'] = tbl['concept_name'].replace(to_replace=self.columns)

            #....melt data
            aux_1 = pd.melt(tbl,id_vars = ['concept_name','categories'], value_vars = tbl.columns[2:-2])
            aux_2 = tbl.drop(columns=tbl.columns[3:-2])

            aux = pd.merge(aux_1,aux_2, on = ['concept_name','categories'], how='left')
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
                hue = 'categories',
                palette= palette_colors,
                ci = None,
                height = 2,
                aspect = 2,
                facet_kws = {
                    'sharey':'row',
                    'sharex':True
                }
            )
            #..figure adjust
            figure.fig.subplots_adjust(hspace=0.5, top=1.05)
            figure.set_titles(
                template = '{row_name}',
                fontdict = {'fontsize':20, 'fontweight':'bold'}
                )
            figure.set_xlabels('Window')
            figure.set_ylabels('')
            figure.tight_layout()
            figure._legend.remove()

            #....configure x axes
            for ax in figure.axes.flat:
                ax.set_xticks(np.arange(1,len(aux['variable'].unique())+1,1))

            #..add slope coeficients
            coefs = aux.groupby(['concept_name','categories'])['m'].max().reset_index()
            coefs_dict = {}
            for index, row in coefs.iterrows():
                concept_name = row['concept_name']
                categories = row['categories']
                m = row['m']
                if concept_name not in coefs_dict:
                    coefs_dict[concept_name] = {}
                coefs_dict[concept_name][categories] = m
           
            for ax, coef in zip(figure.axes.flat, coefs_dict.keys()):
                group_1 = coefs_dict[coef]['No complications'] if 'No complications' in coefs_dict[coef].keys() else 0
                group_2 = coefs_dict[coef]['Novo complications'] if 'Novo complications' in coefs_dict[coef].keys() else 0
                group_3 = coefs_dict[coef]['Existing complications'] if 'Existing complications' in coefs_dict[coef].keys() else 0
                
                ax.annotate(
                    f"Slopes:\nNo:{group_1:.2f} | De novo:{group_2:.2f} | Existing:{group_3:.2f}",
                    xy=(0.05, 0.90),
                    xycoords = 'axes fraction',
                    fontsize = 12
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
            figure.savefig(OUT_PATH+'slope_lineplot_'+group_name+'.png',dpi=300)

            return logging.info(f'{group_name} lineplot saved')
        
        except Exception as e:
            raise logging.error(f'{self._create_plot.__name__} failed. {e}')