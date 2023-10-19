""" slope_plot.py
    This file contains the functions to create slope line plot by window 
    divided by age group (18-44, 45-64, 65>)

Input:
  - data/diabetia.csv
Output:
  - data/visualizations/diabetia_lineplot.png
"""

# Constants
IN_PATH = './data/diabetia.csv'
OUT_PATH = './data/visualizations/diabetia_lineplot.png'
CONFIG_PATH = './scripts2plot/aux_plots/config_plots.json'


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
from scripts2plot.aux_plots import MakeLineplot

# Global variables
config = json.load(open(CONFIG_PATH,'r', encoding='utf-8'))
_lx_measures:dict[str:str] = config['config_lineplot']['columns']
_y_limits:dict[str:list[int,int]] = config['config_lineplot']['y_limits']
_groups:list[str] = config['config_lineplot']['groups']
_palette_colors:dict[str:str] = config['config_lineplot']['palette']


def run():
    try:
        #..read data
        data = pd.read_csv(IN_PATH, low_memory=False, nrows=None)

        #..Do plot
        make_lineplot = MakeLineplot(data=data, columns=_lx_measures, groups = _groups, palette = _palette_colors)
        make_lineplot.create_plot(y_limits = _y_limits)

    except Exception as e:
        raise logging.error(f'Slope lineplot process failed. {e}')

if __name__=='__main__':  
    logging.info(f'{"="*32} SLOPE LINEPLOT IN PROCESS')
    run()
    logging.info(f'{"="*32} SLOPE LINEPLOT IN FINISHED')