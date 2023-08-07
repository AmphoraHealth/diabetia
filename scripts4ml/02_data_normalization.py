"""
INPUT: 
    - csv file
OUTPUT: 
    - csv file
    - pickle transformers
        - normalization
        - standardization
"""

""" feature_selection.py
    This file contains the code for feature selection.
    The list of features to be selected is stored in a json file.

Input:
  - data/hk_database_balanced.csv
Output:
  - data/hk_database_normalized.csv
Additional outputs:
  - Pickle file
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
#from conf.global_constants import NORMALIZATION_METHODS 

# Constants -------------------------------------------------------------------
DB_PATH:str = './data/diabetia.csv'
OUT_PATH:str = './data/diabetia_normalized.csv'
OUT_PATH_PKL:str = './data/diabetia_normalized.pkl'
OUT_PATH_JSON:str = './data/diabetia_normalized.json'

# Import libraries ------------------------------------------------------------
import pandas as pd
import numpy as np
import re
import os
import sys
import json
import pickle
from sklearn.preprocessing import PowerTransformer

ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging

# Code: feature selection -----------------------------------------------------

class DataNormalization:
    
    def __init__(
          self,
          data:pd.DataFrame,
          configFile:dict
          ):
      self.data = data
      self.config = configFile
      self.columnsToTransform = []


    def mainNormalization(self):
       """
       Function to run all required process to normalize and scale data
       """
       try:
          self.columnsIdentification()
          self.normalize()
          
          #..Saving new file
          self.data.to_csv(OUT_PATH)

       except Exception as e:
          return logging.warning(f'{self.mainNormalization.__name__} failed. {e}')
    
    
    def columnsIdentification(self):
       """
       Function to identify data types column values and update self.columns attribute
       """
       self.columnsToTransform = \
        self.config['measuresCols']\
        + self.config['drugsCols']\
        + ['birthdate','years_since_dx']
       return logging.info('Columns indetified')


    def normalize(self) -> pd.DataFrame:
       """
       Function to normalize and standardize data
       """
       try:
          #..Transform definition
          power_transform = PowerTransformer(
              method = 'yeo-johnson',
              standardize = True
            )
          
          #..fitting transformer
          power_transform.fit(self.data[self.columnsToTransform])
          self.data[self.columnsToTransform] = power_transform.transform(self.data[self.columnsToTransform])

          #..Saving pickle
          with open(OUT_PATH_PKL, 'wb') as file:
            pickle.dump(power_transform, file)

          #..Saving columns normalized
          with open(OUT_PATH_JSON, 'w') as file:
            json.dump({"columnsNormalized":self.columnsToTransform}, file, indent=4, ensure_ascii=False)
          
          return logging.info(f'Data normalized')  
       except Exception as e:
          logging.warning(f'{self.normalize.__name__} failed. {e}')
          return pd.DataFrame()
       
    def __str__(self):
       return 'Data normalization'
    


def runDataNormalization():
  """
  Function to run data normaliaztion
  """
  #..Files
  data:pd.DataFrame = pd.read_csv(DB_PATH, low_memory=False, nrows=100)
  columnGroups:dict = json.load(open(f'{ROOT_PATH}/conf/columnGroups.json','r', encoding = 'Utf-8'))

  dataNorm = DataNormalization(
     data = data,
     configFile = columnGroups
  )
  dataNorm.mainNormalization()

  return logging.info('Normalization finished')



if __name__=='__main__':
   logging.info(f'{"="*30} DATA NORMALIZATION STARTS')
   runDataNormalization()
   logging.info(f'{"="*30} DATA NORMALIZATION FINISHED')

