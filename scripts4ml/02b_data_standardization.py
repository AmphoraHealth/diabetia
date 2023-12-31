"""
02b_data_standardization.py
  This file contains the code for data normalization and standardization.

Input:
  - data/diabetia_normalized.csv
  - conf/columnGroups.json
Output:
  - data/diabetia_standardized.csv
Additional outputs:
  - Pickle file
  - json file with col Names in pickle obj
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
import os
import sys
import re
ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging
from libs.global_constants import *

# Constants -------------------------------------------------------------------
DB_PATH:str = f"{S02A_NORMALIZATION}.parquet"
OUT_PATH:str = f"{S02B_STANDARDIZATION}.parquet"
_STANDARDIZATION_METHOD:str = f"{STANDARDIZATION_METHOD}"
OUT_PATH_SCALER:str = f"{S02B_STANDARDIZATION}.pkl"
OUT_PATH_SCALER_JSON:str = f"{S02B_STANDARDIZATION}.json"

# Import libraries ------------------------------------------------------------
import pandas as pd
import numpy as np
import json
import pickle
from aux_02b_data_standardization import scalers
from aux_00_common import *

# Code: data standardization --------------------------------------------------

class DataNormalization:
    """
    This is class is to standardize data from diabetia. It is required to give
    two inputs: 
    - diabetia_normalized.csv
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
      self.scaler = None


    def mainStandardization(self):
       """
       Function to run all required process to normalize and scale data
       """
       try:
          self.columnsIdentification()
          self.standardize()
          
          #..Saving new file
          save_data(self.data, OUT_PATH)

       except Exception as e:
          return logging.warning(f'{self.mainStandardization.__name__} failed. {e}')
    
    
    def columnsIdentification(self):
      """
      Function to identify data types column values and update self.columns attribute
      """
      try: 
        #..Only consider continuos or numerical cols
        self.columnsToTransform = \
        self.config['measuresCols']\
        + self.config['drugsCols']\
        + [
           'birthdate',
           'years_since_dx',
           'count_cx_w',
           'age_at_wx',
           'age_at_wx_ordinal',
           'dx_age_e11',
           'dx_age_e11_ordinal'
           ]
        self.columnsToTransform = [col for col in self.columnsToTransform if col in self.data.columns]
        self.columnsToTransform = [col for col in self.columnsToTransform if bool(re.match('^.*_label$',str(col)))==False]
        self.columnsToTransform = [col for col in self.columnsToTransform if bool(re.match('^.*_ordinal$',str(col)))==False]
        
        #..identify cols with nulls or 0s
        EmptyCols:list[str] = self.data.columns[((self.data==0)|(self.data.isnull())).all()]
        self.columnsToTransform = [col for col in self.columnsToTransform if col not in EmptyCols]
        
        return logging.info(f'{len(self.columnsToTransform)} Columns indetified')
      
      except Exception as e:
         return logging.warning(f'{self.columnsIdentification.__name__} failed. {e}')
       

    def standardize(self):
       """
       Function to standardize data with z-score 
       z = (x-u) / s
       """
       try:
          #..Intialize scaler
          scaler = scalers[_STANDARDIZATION_METHOD]
          scaler.fit(self.data[self.columnsToTransform])

          #..Scale data
          self.data[self.columnsToTransform] = scaler.transform(self.data[self.columnsToTransform])

          #..Save scaler pkl
          save_data(scaler, OUT_PATH_SCALER)
          
          #..Saving columns scaled
          save_data({"columnsStandardized":self.columnsToTransform}, OUT_PATH_SCALER_JSON)
          
          return logging.info(f'Data scaled')  
       
       except Exception as e:
          return logging.error(f'{self.standardize.__name__} failed. {e}')


    def __str__(self):
       return f'Data standardization by {_STANDARDIZATION_METHOD}'
    

def runDataStandardization():
  """
  Function to run data normaliaztion
  """
  #..Files
  data:pd.DataFrame = load_data(DB_PATH)
  columnGroups:dict = load_data(f'{ROOT_PATH}/conf/columnGroups.json')

  #..Initialize normalization and standardization
  dataNorm = DataNormalization(
     data = data,
     configFile = columnGroups
  )

  #..Run process
  dataNorm.mainStandardization()

  return logging.info('Standardization process finished')


if __name__=='__main__':
   logging.info(f'{"="*30} DATA STANDARDIZATION STARTS')
   runDataStandardization()
   logging.info(f'{"="*30} DATA STANDARDIZATION FINISHED')

