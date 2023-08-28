""" 
table_one_records.py
    This file contains the functions to create table one bases on records

Input:
  - data/diabetia.csv
Output:
  - data/table_one_records.csv
Additional outputs:
  - None
"""

# get complication from command line ------------------------------------------
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


class TableOne:

    def __init__(
        self,
        data:pd.DataFrame,
        filterCol:str = None,
        filterValue:str = None,
        name:str=None,
        config_path:str = CONFIG_TABLEONE_PATH,
        in_path:str = IN_PATH,
        out_path:str = OUT_PATH
    ):
        self.data = data[data[filterCol]==filterValue] if filterCol != None else data
        self.filterCol = filterCol
        self.filterValue = filterValue
        self.name = name
        self.CONFIG_PATH = config_path
        self.IN_PATH = in_path
        self.OUT_PATH = out_path
        self.config = json.load(open(self.CONFIG_PATH, 'r', encoding='utf-8'))
    

    def createAgeAtDx(self) -> pd.DataFrame:
        """Function to add Age at T2D diagnosis frame"""
        try:
            #..get group by
            grouped_data = \
                self.data.groupby('dx_age_e11_cat')['id']\
                    .agg(['count',lambda x: x.count()/self.data['id'].count()])\
                    .reset_index()
            grouped_data.columns = ['category','measure','measure_per']

            #..Add final format (col with % and group name)
            grouped_data['value'] = \
                grouped_data\
                    .apply(lambda x: f'{x["measure"]:,.0f} ({x["measure_per"]*100:,.2f}%)',axis=1)
            grouped_data.drop(columns = ['measure','measure_per'],inplace=True)
            grouped_data.insert(0,'name','Age at Dx')

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['Age at Dx'],
                    "category":self.config['categories']['ageAtDx'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            logging.debug(f'Age at T2D Dx added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self.createAgeAtDx.__name__} falied. {e}')
        
    
    def createSex(self) -> pd.DataFrame:
        """Function to add sex frame. From data engineering process 0 = Female and 1 = Male"""
        try:
            #..get group by
            grouped_data = \
                self.data.groupby('cs_sex')['id']\
                    .agg(['count',lambda x: x.count()/self.data['id'].count()])\
                    .reset_index()
            grouped_data.columns = ['category','measure','measure_per']

            #..Add final format (col with % and group name)
            grouped_data['value'] = \
                grouped_data\
                    .apply(lambda x: f'{x["measure"]:,.0f} ({x["measure_per"]*100:,.2f}%)',axis=1)
            grouped_data.drop(columns = ['measure','measure_per'],inplace=True)
            grouped_data.insert(0,'name','Sex')
            grouped_data['category'].replace({0:'Female',1:'Male'},inplace=True) 

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['Sex'],
                    "category":self.config['categories']['sex'].keys()
                }
            )
            
            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            logging.debug(f'Sex added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self.createSex.__name__} falied. {e}')
        

    def createBMI(self) -> pd.DataFrame:
        """Function to create BMI frame. Categories are previously defined by WHO recomendation"""
        try:
            #..default vars
            order:dict[str:int] = self.config['categories']['bmi']

            #..adding aux cols
            self.data['bmi_aux'] = self.data['bmi_label'].copy()
            self.data.loc[:,'bmi_aux'] = \
                self.data['bmi_label']\
                    .replace(
                    {
                        'Obesity (class 1)':'Obesity (any class)',
                        'Obesity (class 2)':'Obesity (any class)',
                        'Obesity (class 3)':'Obesity (any class)'
                    }
                )
            
            #..get group by
            grouped_data = \
                self.data.groupby('bmi_aux')['id']\
                    .agg(['count',lambda x: x.count()/self.data['id'].count()])\
                    .reset_index()
            grouped_data.columns = ['category','measure','measure_per']

            #..Add final format (col with % and group name)
            grouped_data['order'] = grouped_data['category'].apply(lambda x: order.get(x,None))
            grouped_data['value'] = \
                grouped_data\
                    .apply(lambda x: f'{x["measure"]:,.0f} ({x["measure_per"]*100:,.2f}%)',axis=1)
            grouped_data.sort_values(by='order',inplace=True)
            grouped_data.drop(columns = ['measure','measure_per','order'],inplace=True)
            grouped_data.insert(0,'name','BMI')
            
            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['BMI'],
                    "category":self.config['categories']['bmi'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            logging.debug(f'BMI added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self.createBMI.__name__} falied. {e}')
        

    def createT2DComplications(self) -> pd.DataFrame:
        """Function to create T2D complications frame. Only are consider E11.2 to E11.5 ICD codes"""
        try:
            #..default values
            t2d_complications:list[str] = list(self.config['categories']['t2d_complications'].keys())

            #..get group by
            grouped_data = self.data[t2d_complications].sum().reset_index().rename(columns={0:'measure','index':'category'})
            grouped_data['measure_per'] = grouped_data['measure'].apply(lambda x: x/self.data['id'].count())
            
            #..Add final format (col with % and group name)
            grouped_data['value'] = \
                            grouped_data\
                                .apply(lambda x: f'{x["measure"]:,.0f} ({x["measure_per"]*100:,.2f}%)',axis=1)
            grouped_data.drop(columns = ['measure','measure_per'],inplace=True)
            grouped_data.insert(0,'name','T2D Complications')

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['T2D Complications'],
                    "category":self.config['categories']['t2d_complications'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)
            
            logging.debug(f'T2D complications added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self.createT2DComplications.__name__} falied. {e}')


    def createComorbidities(self) -> pd.DataFrame:
        """Function to create comorbidities frame"""
        try:
            #..dafult values
            comorbidities = list(self.config['categories']['comorbidities'].keys())

            #..get groupby
            grouped_data = \
                self.data[comorbidities]\
                    .sum()\
                    .reset_index()\
                    .rename(columns={0:'measure','index':'category'})
            grouped_data['measure_per'] = \
                grouped_data['measure']\
                    .apply(lambda x: x/self.data['id'].count())
            
            #..Add final format (col with % and group name)
            grouped_data['value'] = \
                            grouped_data\
                                .apply(lambda x: f'{x["measure"]:,.0f} ({x["measure_per"]*100:,.2f}%)',axis=1)
            grouped_data.drop(columns = ['measure','measure_per'],inplace=True)
            grouped_data.insert(0,'name','Comorbidities')            

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['Comorbidities'],
                    "category":self.config['categories']['comorbidities'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)
            
            logging.debug(f'Comorbidited added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self.createComorbidities.__name__} falied. {e}')
        

    def createLaboratories(self) -> pd.DataFrame:
        """
        Function to create laboratories frame. This frame use values cleaned in data engineering: *_value
        and consider median and std to give a final result
        """
        try:
            #..dafult values
            lxCols:list[str] = list(self.config['categories']['laboratories'].keys())
            #..get groupby
            grouped_data = \
                self.data[lxCols]\
                    .replace(0,np.nan)\
                    .agg(['median','std'])\
                    .T\
                    .reset_index()\
                    .rename(columns={'index':'category'})
            
            #..Add final format (col with % and group name)
            grouped_data['category'] = grouped_data['category'].replace('fn_creatinine_median','creatinine_value')
            grouped_data['value'] = \
                        grouped_data\
                            .apply(lambda x: f'{x["median"]:,.2f} ({x["std"]:,.2f})',axis=1)
            grouped_data.drop(columns=['median','std'],inplace=True)
            grouped_data.insert(0,'name','Laboratories')  

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['Laboratories'],
                    "category":self.config['categories']['laboratories'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)
            
            logging.debug(f'Laboratories added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self.createLaboratories.__name__} falied. {e}')
        

    def createGFR(self) -> pd.DataFrame:
        """Function to crate GFR frame"""
        try:
            #..default vars
            order:dict[str:int] = self.config['categories']['gfr']

            #..adding aux cols
            self.data['gfr_aux'] = self.data['creatinine_label'].copy()
            self.data.loc[:,'gfr_aux'] = \
                self.data['creatinine_label']\
                    .replace(
                    {
                        'G1':'G1-G2',
                        'G2':'G1-G2',
                        'G3a':'G3',
                        'G3b':'G3',
                        'G4':'G4-G5',
                        'G5':'G4-G5'
                    }
                )
            
            #..get group by
            grouped_data = \
                self.data.groupby('gfr_aux')['id']\
                    .agg(['count',lambda x: x.count()/self.data['id'].count()])\
                    .reset_index()
            grouped_data.columns = ['category','measure','measure_per']

            #..Add final format (col with % and group name)
            grouped_data['order'] = grouped_data['category'].apply(lambda x: order.get(x,None))
            grouped_data['value'] = \
                grouped_data\
                    .apply(lambda x: f'{x["measure"]:,.0f} ({x["measure_per"]*100:,.2f}%)',axis=1)
            grouped_data.sort_values(by='order',inplace=True)
            grouped_data.drop(columns = ['measure','measure_per','order'],inplace=True)
            grouped_data.insert(0,'name','GFR')

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {   
                    "name":['GFR'],
                    "category":self.config['categories']['gfr'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)
            
            logging.debug(f'GFR added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self.createGFR.__name__} falied. {e}')
        

    def create(self) -> pd.DataFrame:
        """Function to run all frames and concatenate a final frame"""
        try:
            #..Get intial frame
            valueName:str = 'value' if self.name == None else self.name
            global_frame:pd.DataFrame = pd.DataFrame(
                {
                    'name':[self.filterValue],
                    'category':['N'],
                    valueName:[self.data.shape[0]]
                }
            )

            #..Get frames by category
            frame_ageAtDx = self.createAgeAtDx()
            frame_sex = self.createSex()
            frame_bmi = self.createBMI()
            frame_complications = self.createT2DComplications()
            frame_comorbidities = self.createComorbidities()
            frame_laboratories = self.createLaboratories()
            frame_gfr = self.createGFR()

            #..Concat all
            data:pd.DataFrame = pd.concat(
                [
                    global_frame,
                    frame_ageAtDx,
                    frame_sex,
                    frame_bmi,
                    frame_complications,
                    frame_comorbidities,
                    frame_laboratories,
                    frame_gfr
                ],
                axis=0
            )

            logging.info(f'All charecteristics of table one created for {self.name}')
            return data
        except Exception as e:
            raise logging.error(f'{self.create.__name__} falied. {e}')
        

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    data = pd.read_csv('./data/diabetia.csv',low_memory=False,nrows=100)
    tableone = TableOne(data=data)
    tableone.create()
    