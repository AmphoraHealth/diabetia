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
        1. Age at first visit: age calculated at the first visit registered
        2. Age at Dx: age calculated at the year of T2D diagnosis
        3. Sex: sex of patient
        4. BMI_median: median result in first window
        5. T2D complications: in first window
        6. Comorbidities: in first window
        7. Laboratory values: median in first window
        8. GFR: result in first window
        """
        return self._transform()
    

    def _transform(self) -> pd.DataFrame:
        try:
            #..Preprocess required
            self._cleanLaboratories()

            #..auxiliar cols
            self.data['cx_curp'] = self.data['id'].apply(lambda x: x.split('-')[0])
            self.data['window'] = self.data['id'].apply(lambda x: x.split('-')[1])
            self.data['window'] = self.data['window'].astype(int)

            #..sorting values
            self.data = self.data.sort_values(by=['cx_curp','window'], ascending = True).reset_index()

            #..Do new dataframe summariezed
            tbl:pd.DataFrame = self._uniquePatients()

            #..Do summarized  values
            tbl = self._summarizeAgeAtFirstVisit(tbl=tbl)
            tbl = self._summarizeAgeAtDx(tbl=tbl)
            tbl = self._summarizeSex(tbl=tbl)
            tbl = self._summarizeBMI(tbl=tbl)
            tbl = self._summarizeT2DComplications(tbl=tbl)
            tbl = self._summarizeComorbidites(tbl=tbl)
            tbl = self._summariezeLaboratories(tbl=tbl)
            tbl = self._summarizeGFR(tbl=tbl)

            tbl.rename(columns={'cx_curp':'id'},inplace=True)
            
            logging.info('Data summarized')
            return tbl
        except Exception as e:
            logging.error(f'{self._transform.__name__} failed. {e}')
        return


    def _cleanLaboratories(self):
        """
        This function clean up values in 0 for laboratories used:
        - Creatinine
        - Glucose
        - Hemoglobin
        - Triglycerides
        - Cholesterol

        Return value is an update of self.data parameter
        """
        try:
            #..dafult values
            lxCols:list[str] = list(self.config['categories']['laboratories']['columnsUsed'])

            #..replace 0 for np.nan
            self.data[lxCols] = \
                self.data[lxCols]\
                    .replace(0,np.nan)
            return logging.debug('Laboratories cleaned up')    
        except Exception as e:
            raise logging.error(f'{self._cleanLaboratories.__name__} failed. {e}')
        

    def _uniquePatients(self) -> pd.DataFrame:
        """Drop duplicates by cx_curp auxiliar col generated in _transform"""
        t2d:list[str] = ['diabetes_mellitus_type_2']
        return self.data[['cx_curp']+t2d].drop_duplicates(subset='cx_curp', keep='first')
    

    def _summarizeAgeAtFirstVisit(self,tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped AgeAtDx
            summ = (
                self.data[['window','cx_curp','age_at_wx']]
                    .drop_duplicates(subset='cx_curp',keep='first')
                )
            
            #..merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            tbl.drop(columns='window',inplace=True)
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summarizeAgeAtFirstVisit.__name__} failed. {e}')


    def _summarizeAgeAtDx(self,tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped AgeAtDx
            summ = (
                self.data[['window','cx_curp','dx_age_e11_cat']]
                    .drop_duplicates(subset='cx_curp', keep='first')
                )
                        
            #..merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            tbl.drop(columns='window',inplace=True)
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summarizeAgeAtDx.__name__} failed. {e}')
        

    def _summarizeSex(self,tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped Sex
            summ = (
                self.data[['cx_curp','cs_sex']]
                    .dropna(subset='cs_sex')
                    .drop_duplicates()
                )
            
            #..merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summarizeSex.__name__} failed. {e}')


    def _summarizeBMI(self,tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped BMI
            summ = (
                self.data[['cx_curp','bmi_label']]
                    .dropna(subset='bmi_label')
                    .drop_duplicates(subset='cx_curp', keep='first')
                )
            
            #..merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summarizeAgeAtDx.__name__} failed. {e}')
    

    def _summarizeT2DComplications(self,tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped T2D complications
            complications:list[str] = list(self.config['categories']['t2d_complications']['columnsUsed'])
            summ = (
                self.data[['cx_curp']+complications]
                    .drop_duplicates(subset='cx_curp', keep='first')
                )
            
            #..Merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summarizeT2DComplications.__name__} failed. {e}')


    def _summarizeComorbidites(self,tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped comorbidities
            comorbiditiesCols:list[str] = list(self.config['categories']['comorbidities']['columnsUsed'])
            summ = (
                self.data[['cx_curp']+comorbiditiesCols]
                    .drop_duplicates(subset='cx_curp', keep='first')
                )
            
            #..Merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summarizeComorbidites.__name__} failed. {e}')
    

    def _summariezeLaboratories(self, tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped Laboratories
            lx:list[str] = list(self.config['categories']['laboratories']['columnsUsed'])
            summ = self.data[['window','cx_curp']+lx].copy()
            summ[lx] = summ.groupby('cx_curp')[lx].bfill()
            summ =  summ.drop_duplicates(subset='cx_curp', keep='first')
            
            #..Merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            tbl.drop(columns='window',inplace=True)
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summariezeLaboratories.__name__} failed. {e}')
    

    def _summarizeGFR(self,tbl:pd.DataFrame) -> pd.DataFrame:
        try:
            #..grouped GFR
            summ = self.data[['window','cx_curp','creatinine_label']].copy()
            summ['creatinine_label'] = summ.groupby('cx_curp')['creatinine_label'].bfill()
            summ =  summ.drop_duplicates(subset='cx_curp', keep='first')
            
            #..Merge to tbl
            tbl = pd.merge(
                tbl,
                summ,
                on = 'cx_curp',
                how = 'left'
            )
            tbl.drop(columns='window',inplace=True)
            return tbl
        except Exception as e:
            raise logging.error(f'{self._summarizeAgeAtDx.__name__} failed. {e}')
    
    