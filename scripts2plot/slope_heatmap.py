""" slope_plot.py
    This file contains the functions to create slope line plot by window 
    divided by age group (18-44, 45-64, 65>)

Input:
  - data/diabetia.csv
Output:
  - data/visualizations/diabetia_lineplot.png
"""

# Import libraries
import pandas as pd
import os
import sys
import json

# Import local libraries
ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging
from scripts2plot.aux_plots import MakeHeatmap

# Constants
IN_PATH = './data/diabetia.csv'
CONFIG_PATH = './scripts2plot/aux_plots/config_plots.json'

# Global variables
config:dict = json.load(open(CONFIG_PATH, 'r', encoding='utf-8'))
_lx_measures:dict[str:str] = config['config_heatmap']['columns']
_groups:list[str] = config['config_heatmap']['groups']
_categories:dict[float:str] = config['config_heatmap']['categories']

def run():
    try:
        #..read data
        data = pd.read_csv(IN_PATH, low_memory=False, nrows=None)

        #..Do plot
        make_heatmap = MakeHeatmap(
            data=data,
            columns=_lx_measures,
            groups=_groups,
            categories=_categories
        )
        make_heatmap.create_plot()

    except Exception as e:
        raise logging.error(f'Slope heatmap process failed. {e}')

if __name__=='__main__':  
    logging.info(f'{"="*32} SLOPE HEATMAP IN PROCESS')
    run()
    logging.info(f'{"="*32} SLOPE HEATMAP IN FINISHED')