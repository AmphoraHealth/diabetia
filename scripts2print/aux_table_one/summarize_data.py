import os
import sys
ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging

# Constants
IN_PATH = 'data/diabetia.csv'
OUT_PATH = 'data/table_one_records.csv'
CONFIG_PATH = 'conf/columnGroups.json'
CONFIG_TABLEONE_PATH = 'scripts2print/aux_table_one/config_tableone.json'

# Import libraries
import pandas as pd
import numpy as np
import json
import re
import janitor

#..Default configurations
import warnings
warnings.filterwarnings("ignore")

class SummarizeData:

    def __init__(
        self,
        data:pd.DataFrame,
        config_path:str = None,
    ):
        #..assertions
        assert data.shape[0] > 0, 'Data input is missing or data is empty'
        assert os.path.exists(config_path), 'Config path not found.'
        
        #..initial parameters
        self.data = data
        self.CONFIG_PATH:str = config_path
        self.config = json.load(open(self.CONFIG_PATH, 'r', encoding='utf-8'))
        

    def transform(self) -> pd.DataFrame:
        """
        This function summarize data from diabetia.csv. 
        Next are the considerations for each category that will be processed
        by table_one.py script for patients.
        1. Sex: sex of patient
        2. Age at Dx: age calculated at the year of T2D diagnosis
        3. BMI_median: median result in first window
        4. T2D complications: in first window
        5. Comorbidities: in first window
        6. Laboratory values: median in first window
        7. GFR: result in first window
        """
        return self._transform()
    

    def _transform(self) -> pd.DataFrame:
        try:
            pass
        except Exception as e:
            logging.error(f'{self._transform.__name__} failed. {e}')
        return  
    

if __name__=='__main__':
    data = pd.read_csv('./data/diabetia.csv',low_memory=False,nrows=100)
    summarize = SummarizeData(
        data = data,
        config_path=CONFIG_TABLEONE_PATH
        )
    data = summarize.transform()
    