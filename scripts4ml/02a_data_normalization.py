"""
02a_data_normalization.py
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
import os
import sys
ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging
#from conf.global_constants import S02_NORMALIZATION

# Constants -------------------------------------------------------------------
DB_PATH:str = './data/diabetia.csv'
OUT_PATH:str = './data/diabetia_normalized.csv'
NORMALIZATION_METHOD:str = 'yeo_johnson'
OUT_PATH_NORMALIZER:str = './data/normalizer.pkl'
OUT_PATH_NORMALIZER_JSON:str = './data/normalizer_columns.json'

# Import libraries ------------------------------------------------------------
import pandas as pd
import numpy as np
import os
import sys
import json
import pickle
from aux_02_data_normalization import normalizers

# Code: data normalization ----------------------------------------------------

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


    def mainNormalization(self):
       """
       Function to run all required process to normalize and scale data
       """
       try:
          self.columnsIdentification()
          self.normalize()
          
          #..Saving new file
          self.data.to_csv(OUT_PATH, index = False)

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
        + [
           'birthdate',
           'years_since_dx',
           'count_cx_w',
           'age_at_wx',
           'age_diag'
           ]

        #..identify cols with nulls or 0s
        EmptyCols:list[str] = self.data.columns[((self.data==0)|(self.data.isnull())).all()]
        self.columnsToTransform = [col for col in self.columnsToTransform if col not in EmptyCols]
        
        return logging.info(f'{len(self.columnsToTransform)} Columns indetified')
      
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
          return logging.warning(f'{self.normalize.__name__} failed. {e}')
          
          
       

    def __str__(self):
       return f'Data normalization by {NORMALIZATION_METHOD}'
    

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

  return logging.info('Normalization process finished')


if __name__=='__main__':
   logging.info(f'{"="*30} DATA NORMALIZATION STARTS')
   runDataNormalization()
   logging.info(f'{"="*30} DATA NORMALIZATION FINISHED')

