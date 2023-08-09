"""
02_data_normalization.py
  This file contains the code for data normalization and standardization.

Input:
  - data/diabetia_balanced.csv
  - conf/columnGroups.json
Output:
  - data/diabetia_normalized.csv
Additional outputs:
  - Pickle file
  - json file with col Names in pickle obj
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
#from conf.global_constants import NORMALIZATION_METHODS 

# Constants -------------------------------------------------------------------
DB_PATH:str = './data/diabetia.csv'
OUT_PATH:str = './data/diabetia_normalized.csv'
NORMALIZATION_METHOD:str = 'yeo_johnson'
STANDARDIZATION_METHOD:str = 'z_score'
OUT_PATH_NORMALIZER:str = './data/diabetia_normalizer.pkl'
OUT_PATH_NORMALIZER_JSON:str = './data/diabetia_normalizer.json'
OUT_PATH_SCALER:str = './data/diabetia_scaler.pkl'
OUT_PATH_SCALER_JSON:str = './data/diabetia_scaler.json'

# Import libraries ------------------------------------------------------------
import pandas as pd
import numpy as np
import re
import os
import sys
import json
import pickle
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import QuantileTransformer
from sklearn.preprocessing import StandardScaler
from aux_02_data_normalization import normalizers
from aux_02_data_normalization import scalers

ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging

# Code: data normalization and standardization -----------------------------------------------------

class DataNormalization:
    """
    This is class is to normalize and standardize data from diabetia. It is required to give
    two inputs: 
    - diabetia_balanced.csv
    - columnGroups.json

    With json file, dtypes of cols will be identify to process only continues data. In next versions
    process to categorical and binary cols may be upload. 
    """
    
    def __init__(
          self,
          data:pd.DataFrame,
          configFile:dict,
          ):
      
      self.data = data
      self.config = configFile
      self.columnsToTransform = []
      self.normalizer = None
      self.scaler = None


    def mainNormalization(self):
       """
       Function to run all required process to normalize and scale data
       """
       try:
          self.columnsIdentification()
          self.normalize()
          self.standardize()
          
          #..Saving new file
          self.data.to_csv(OUT_PATH)

       except Exception as e:
          return logging.warning(f'{self.mainNormalization.__name__} failed. {e}')
    
    
    def columnsIdentification(self):
      """
      Function to identify data types column values and update self.columns attribute
      """
      try: 
        #..Only consider continuos or numerical cols
        self.columnsToTransform = \
        self.config['measuresCols']\
        + self.config['drugsCols']\
        + ['birthdate','years_since_dx']
        
        return logging.info('Columns indetified')
      
      except Exception as e:
         return logging.warning(f'{self.columnsIdentification.__name__} failed. {e}')
        

    def normalize(self):
       """
       Function to normalize by Yeo-Johnson
       """
       try:
          #..Initialize PowerTransformer
          normalizer = normalizers[NORMALIZATION_METHOD]
          
          #..fitting transformer
          normalizer.fit(self.data[self.columnsToTransform])
          self.data[self.columnsToTransform] = normalizer.transform(self.data[self.columnsToTransform])

          #..Saving pickle
          with open(OUT_PATH_NORMALIZER, 'wb') as file:
            pickle.dump(normalizer, file)

          #..Saving columns normalized
          with open(OUT_PATH_NORMALIZER_JSON, 'w') as file:
            json.dump({"columnsNormalized":self.columnsToTransform}, file, indent=4, ensure_ascii=False)
          
          return logging.info(f'Data normalized')  
       
       except Exception as e:
          logging.warning(f'{self.normalize.__name__} failed. {e}')
          return pd.DataFrame()
       

    def standardize(self):
       """
       Function to standardize data with z-score 
       z = (x-u) / s
       """
       try:
          #..Intialize scaler
          scaler = scalers[STANDARDIZATION_METHOD]
          scaler.fit(self.data[self.columnsToTransform])

          #..Scale data
          self.data[self.columnsToTransform] = scaler.transform(self.data[self.columnsToTransform])

          #..Save sacaler pkl
          with open(OUT_PATH_SCALER, 'wb') as file:
            pickle.dump(scaler, file)
          
          #..Saving columns scaled
          with open(OUT_PATH_SCALER_JSON, 'w') as file:
            json.dump({"columnsScaled":self.columnsToTransform}, file, indent=4, ensure_ascii=False)
          
          return logging.info(f'Data scaled')  
       
       except Exception as e:
          logging.warning(f'{self.standardize.__name__} failed. {e}')


    def __str__(self):
       return 'Data normalization and standardization'
    

def runDataNormalization():
  """
  Function to run data normaliaztion
  """
  #..Files
  data:pd.DataFrame = pd.read_csv(DB_PATH, low_memory=False, nrows=None)
  columnGroups:dict = json.load(open(f'{ROOT_PATH}/conf/columnGroups.json','r', encoding = 'Utf-8'))

  #..Initialize normalization and standardization
  dataNorm = DataNormalization(
     data = data,
     configFile = columnGroups
  )

  #..Run process
  dataNorm.mainNormalization()

  return logging.info('Normalization finished')


if __name__=='__main__':
   logging.info(f'{"="*30} DATA NORMALIZATION STARTS')
   runDataNormalization()
   logging.info(f'{"="*30} DATA NORMALIZATION FINISHED')

