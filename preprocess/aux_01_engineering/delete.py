# Import libraries
import pandas as pd
import os
import sys
import re

ROOT_PATH:str = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging

class DeleteFunctions:
    def dropCols(self):
        """
        Function to drop next columns:
        - unnecesary columns or informative
        - empty columns
        - all columns that are counts
        - drop std (pending)
        """   
        try:
            #..Drop unncessesary columns by json file
            dropUnnecessaryCols:list[str] = self.config['config']['columnsToDrop']['unnecessaryCols']
            self.data.drop(columns=dropUnnecessaryCols, inplace=True)

            #..Drop empty columns (Zero or NaN) 
            dropEmptyCols:list[str] = self.data.columns[((self.data==0)|(self.data.isnull())).all()]
            self.data.drop(columns=dropEmptyCols, inplace=True)

            #..Drop counts
            dropCountColumns:list[str] = [n for n in self.data.columns if bool(re.match('^.*count$',n)) == True]
            self.data.drop(columns=dropCountColumns, inplace=True)

            columnsDropped:int = len(dropUnnecessaryCols)\
                +len(dropEmptyCols)\
                +len(dropCountColumns)
            
            return logging.info(f'{columnsDropped} columns dropped')
        
        except Exception as e:
            raise logging.error(f'{self.dropCols.__name__} failed. {e}')


    def dropRows(self):
        """
        Function to drop rows: 
        - where count_cx_w == 0
        """
        try:
            #..drop rows without consults reported.
            intialRows:int = self.data.shape[0] 
            self.data = self.data[(self.data['count_cx_w']!=0)&(self.data['count_cx_w'].isnull()==False)]

            logging.info(f'{intialRows-self.data.shape[0]} rows with 0 consults dropped.')
        except Exception as e:
            raise logging.error(f'{self.dropRows.__name__} failed. {e}')