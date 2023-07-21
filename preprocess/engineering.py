""" enginering.py
    This file contains the functions for data cleaning and feature enginering.
    - remove unnecessary columns
    - one-hot encoding (if needed)

Input:
  - data/hk_database.csv
Output:
  - data/hk_database_cleaned.csv
Additional outputs:
  - None
"""

# Constants
IN_PATH = '../data/hk_database.csv'
OUT_PATH = '../data/hk_database_cleaned.csv'
CONFIG_PATH = '../conf/engineering_conf.json'

# Import libraries
import pandas as pd
import numpy as np
import re
import os
import logging
import json
from sklearn import preprocessing

#..Default configurations
logging_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format, datefmt='%d-%m-%y %H:%M:%S')

class DataEngineering:
    
    def __init__(
        self,
        IN_PATH:str,
        CONFIG_PATH:str
      ):
        self.in_path:str = IN_PATH
        self.config_path:str = CONFIG_PATH
        self.data:pd.dataFrame = pd.DataFrame()
        self.config:dict = json.load(open(f'{self.config_path}', 'r'))
    

    def readFile(self):
        try:
            return logging.info('File read')
        except Exception as e:
            return logging.warning(f'File was not read. {e}')
          
    
    def dropCols(self):
        """
        Function to drop next columns:
        - unnecesary columns or informative
        - empty columns
        - all columns that are counts
        """   
        try:
            return logging.info(f'{0} columns dropped')
        except Exception as e:
            return logging.warning(f'Columns were not dropped. {e}')
        

    def categoricalCols(self):
        """
        Function to clean categorical columns. It is required to write in engineering_conf
        the columns which are consider as categorical. For this columns will be transformed into
        labels with LabelEnconder from sklearn.
        """
        try:
            return logging.info('Categorical cols transformed')
        except Exception as e:
            return logging.warning(f'{self.categoricalCols.__name__} failed. {e}')
    

    def updateDiagnosis(self): 
        """
        Function to change the Y variables into multilabel vars depending on the case it represents
        (Y vars are include also in X vars). 
        The cases are classified as follow:
        Considering [X,Y]:
        1. [0,0] = 0
        2. [0,1] = 1
        3. [1,1] = 2
        """  
        try:
            return logging.info(f'{0} columns dropped')
        except Exception as e:
            return logging.warning(f'Columns were not dropped. {e}')
        

    def transform(self) -> pd.DataFrame:
        """
        Function to run all transformations.
        """
        try:
            logging.info('Transformations done')
            return self.data
        except Exception as e:
            return logging.warning(f'Transformations failed. {e}')
    

    def __str__(self):
        return 'Data engineering transformations'


def run() -> pd.DataFrame:
    """
    Function to run all data engineering process
    """
    # intialize class
    try:
      data_engineering = DataEngineering(
          IN_PATH=IN_PATH,
          CONFIG_PATH=CONFIG_PATH
      )

      # Run transformations
      data = data_engineering.transform()

      # Save file
      data.to_csv(f'{OUT_PATH}', index=False, encoding='UTF-8')
      
      return logging.info(f'File saved on {OUT_PATH}')
    
    except Exception as e:
        return logging.warning(f'{run.__name__} process failed. {e}')


if __name__ == '__main__':
    logging.info(f'{"="*30}DATA ENGINEERING STARTS')
    run()
    logging.info(f'{"="*30}DATA ENGINEERING FINISHED')