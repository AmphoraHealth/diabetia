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
IN_PATH = './data/hk_database.csv'
OUT_PATH = './data/hk_database_cleaned.csv'
CONFIG_PATH = './conf/engineering_conf.json'

# Import libraries
import pandas as pd
import numpy as np
import re
import os
import json
import sys
from sklearn import preprocessing
from alive_progress import alive_bar
from aux_01_engineering import CleanFunctions
from aux_01_engineering import CreateFunctions
from aux_01_engineering import DeleteFunctions
from aux_01_engineering import UpdateFunctions

ROOT_PATH:str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.logging import logging


class DataEngineering(
    CleanFunctions,
    CreateFunctions,
    UpdateFunctions,
    DeleteFunctions
    ):
    
    def __init__(
        self,
        IN_PATH:str,
        CONFIG_PATH:str
      ):
        self.in_path:str = IN_PATH
        self.config_path:str = CONFIG_PATH
        self.data:pd.DataFrame = pd.DataFrame()
        self.config:dict = json.load(open(f'{self.config_path}', 'r', encoding='UTF-8'))
    
    def readFile(self,rows:int = None):
        try:
            self.data = pd.read_csv(f'{self.in_path}', low_memory=False, nrows=None)
            return logging.info('File read')
        except Exception as e:
            raise logging.warning(f'File was not read. {e}')
        

    def mainTransform(self) -> pd.DataFrame:
        """
        Function to run all transformations.
        """
        try:
          #..Transformations starts
          self.readFile()

          #..clean functions
          self.translateColumns()
          self.cleanHeaders()
          self.cleanCareunit()

          #..create functions
          self.createAgeDxGroup()
          self.createYearSinceDx()
          self.createBmiCategory()
          self.createGlucoseCategory()
          self.createHemoglobinCategory()
          self.createTriglyceridesCategory()
          self.createCreatinineCategory()
          self.createCholesterolCategory()
          self.categoricalCols()
          self.ordinalCols()

          #..update functions
          self.updateDiagnosis()

          #..delete functions
          self.dropCols()

          logging.info('Transformations done')
          return self.data
        except Exception as e:
            raise logging.warning(f'Transformations failed. {e}')
            

    def __str__(self):
        return 'Data engineering main process. It uses functions from DataEngieneeringFunctions'


def runDataEngineering() -> pd.DataFrame:
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
      data = data_engineering.mainTransform()

      # Save file
      data.to_csv(f'{OUT_PATH}', index=False, encoding='UTF-8')
      
      return logging.info(f'File saved on {OUT_PATH}')
    
    except Exception as e:
        raise logging.warning(f'{runDataEngineering.__name__} process failed. {e}')


if __name__ == '__main__':
    logging.info(f'{"="*30}DATA ENGINEERING STARTS')
    runDataEngineering()
    logging.info(f'{"="*30}DATA ENGINEERING FINISHED')