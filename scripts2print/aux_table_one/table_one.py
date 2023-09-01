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
        config_path:str = CONFIG_TABLEONE_PATH
    ):
        self.data = data[data[filterCol]==filterValue] if filterCol != None else data
        self.filterCol = filterCol
        self.filterValue = filterValue
        self.name = name
        self.CONFIG_PATH = config_path
        self.config = json.load(open(self.CONFIG_PATH, 'r', encoding='utf-8'))
    

    def create(self) -> pd.DataFrame:
        """
        This function create a table one from diabetia.csv database. It is necessary
        to give as input: 
        - data (diabetia.csv database after preprocessing pipeline)
        - filterCol (column to apply filter)
        - filter Value (value to filter in filterCol)
        - name (name to rename output)
        - config_path (path to read table one configurations)
        
        Each category has its own function and all are applied in _create() function. 
        Defined categories are next:
        - Age at first visit: count(%)
            18-44
            45-64
            65>
        - Age at T2D diagnosis in categories: count(%)
            18-44
            45-64
            65>
        - Sex: count(%)
            Female
            Male
        - BMI by category: count(%)
            Underweight
            Normal weight
            Overweight
            Obesity (any class)
        - T2D complications: count(%)
            type_2_diabetes_mellitus_with_renal_complications
            type_2_diabetes_mellitus_with_ophthalmic_complications
            type_2_diabetes_mellitus_with_neurological_complications
            type_2_diabetes_mellitus_with_peripheral_circulatory_complications
        - Comorbidities: count(%)
            essential_(primary)_hypertension
            disorders_of_lipoprotein_metabolism_and_other_lipidemias
        - Laboratories: mean (std)
            creatinine_value
            glucose_value
            hemoglobin_value
            triglycerides_value
            cholesterol_value
        """
        return self._create()
    
    
    def _create(self) -> pd.DataFrame:
        """Function to run all frames and concatenate a final frame"""
        try:
            #..Get intial frame
            valueName:str = 'value' if self.name == None else self.name
            global_frame:pd.DataFrame = pd.DataFrame(
                {
                    'name':[self.filterValue],
                    'category':['N'],
                    valueName:["{:,.0f}".format(self.data.shape[0])]
                }
            )

            #..Get frames by category
            frame_ageAtFirstVisit = self._createAgeAtFirstVisit()
            frame_ageAtDx = self._createAgeAtDx()
            frame_sex = self._createSex()
            frame_bmi = self._createBMI()
            frame_complications = self._createT2DComplications()
            frame_comorbidities = self._createComorbidities()
            frame_laboratories = self._createLaboratories()

            #..Concat all
            data:pd.DataFrame = pd.concat(
                [
                    global_frame,
                    frame_ageAtFirstVisit,
                    frame_ageAtDx,
                    frame_sex,
                    frame_bmi,
                    frame_complications,
                    frame_comorbidities,
                    frame_laboratories,
                ],
                axis=0
            )

            logging.info(f'All charecteristics of table one created for {self.name}')
            return data
        except Exception as e:
            raise logging.error(f'{self.create.__name__} falied. {e}')
        

    def _createAgeAtFirstVisit(self) -> pd.DataFrame:
        """Function to add Age at first visit"""
        try:
            #..create auxliar col for age_cat
            self.data['age_at_wx_cat'] = pd.cut(
                self.data['age_at_wx'],
                bins = [18,45,65,150],
                right = False,
                labels = ['18-44','45-64','65>']
            )

            #..get group by
            grouped_data = \
                self.data.groupby('age_at_wx_cat')['id']\
                    .agg(['count',lambda x: x.count()/self.data['id'].count()])\
                    .reset_index()
            grouped_data.columns = ['category','measure','measure_per']

            #..Add final format (col with % and group name)
            grouped_data['value'] = \
                grouped_data\
                    .apply(lambda x: f'{x["measure"]:,.0f} ({x["measure_per"]*100:,.2f}%)',axis=1)
            grouped_data.drop(columns = ['measure','measure_per'],inplace=True)
            grouped_data.insert(0,'name','Age at first visit')

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['Age at first visit'],
                    "category":self.config['categories']['ageAtFirstVisit']['order'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            #..Add principal row for formatter
            grouped_data = pd.concat(
                [
                    pd.DataFrame({'name':['Age at first visit']}),
                    grouped_data
                ],
                axis = 0
                ).reset_index(drop=True)

            logging.debug(f'Age at first visit added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self._createAgeAtFirstVisit.__name__} falied. {e}')


    def _createAgeAtDx(self) -> pd.DataFrame:
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
                    "category":self.config['categories']['ageAtDx']['order'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            #..Add principal row for formatter
            grouped_data = pd.concat(
                [
                    pd.DataFrame({'name':['Age at Dx']}),
                    grouped_data
                ],
                axis = 0
                ).reset_index(drop=True)

            logging.debug(f'Age at T2D Dx added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self._createAgeAtDx.__name__} falied. {e}')
        
    
    def _createSex(self) -> pd.DataFrame:
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
                    "category":self.config['categories']['sex']['order'].keys()
                }
            )
            
            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            #..Add principal row for formatter
            grouped_data = pd.concat(
                [
                    pd.DataFrame({'name':['Sex']}),
                    grouped_data
                ],
                axis = 0
                ).reset_index(drop=True)

            logging.debug(f'Sex added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self._createSex.__name__} falied. {e}')
        

    def _createBMI(self) -> pd.DataFrame:
        """Function to create BMI frame. Categories are previously defined by WHO recomendation"""
        try:
            #..default vars
            order:dict[str:int] = self.config['categories']['bmi']['order']

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
                    "category":self.config['categories']['bmi']['order'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            #..Add principal row for formatter
            grouped_data = pd.concat(
                [
                    pd.DataFrame({'name':['BMI']}),
                    grouped_data
                ],
                axis = 0
                ).reset_index(drop=True)

            logging.debug(f'BMI added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self._createBMI.__name__} falied. {e}')
        

    def _createT2DComplications(self) -> pd.DataFrame:
        """Function to create T2D complications frame. Only are consider E11.2 to E11.5 ICD codes"""
        try:
            #..default values
            t2d_complications:list[str] = list(self.config['categories']['t2d_complications']['columnsUsed'])

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
                    "category":t2d_complications
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            #..Add principal row for formatter
            grouped_data = pd.concat(
                [
                    pd.DataFrame({'name':['T2D Complications']}),
                    grouped_data
                ],
                axis = 0
                ).reset_index(drop=True)
            
            logging.debug(f'T2D complications added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self._createT2DComplications.__name__} falied. {e}')


    def _createComorbidities(self) -> pd.DataFrame:
        """Function to create comorbidities frame"""
        try:
            #..dafult values
            comorbidities:list[str] = list(self.config['categories']['comorbidities']['columnsUsed'])

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
                    "category":comorbidities
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            #..Add principal row for formatter
            grouped_data = pd.concat(
                [
                    pd.DataFrame({'name':['Comorbidities']}),
                    grouped_data
                ],
                axis = 0
                ).reset_index(drop=True)
            
            logging.debug(f'Comorbidited added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self._createComorbidities.__name__} falied. {e}')
        

    def _createLaboratories(self) -> pd.DataFrame:
        """
        Function to create laboratories frame. This frame use values cleaned in data engineering: *_value
        and consider median and std to give a final result
        """
        try:
            #..dafult values
            lxCols:list[str] = list(self.config['categories']['laboratories']['columnsUsed'])

            #..get groupby
            grouped_data = \
                self.data[lxCols]\
                    .replace(0,np.nan)\
                    .agg(['mean','std'])\
                    .T\
                    .reset_index()\
                    .rename(columns={'index':'category'})
            
            #..Add final format (col with % and group name)
            replaces:dict = {
                'fn_creatinine_mean':'creatinine_value',
                'glucose_value_mean':'glucose_value',
                'fn_hemoglobin_mean':'hemoglobin_value',
                'fn_triglycerides_mean':'triglycerides_value',
                'fn_cholesterol_mean':'cholesterol_value'
            }
            grouped_data['category'] = grouped_data['category'].replace(to_replace=replaces)
            grouped_data['value'] = \
                        grouped_data\
                            .apply(lambda x: f'{x["mean"]:,.2f} ({x["std"]:,.2f})',axis=1)
            grouped_data.drop(columns=['mean','std'],inplace=True)
            grouped_data.insert(0,'name','Laboratories')  

            #..Complete janitor process
            grouped_data = grouped_data.complete(
                {
                    "name":['Laboratories'],
                    "category":self.config['categories']['laboratories']['order'].keys()
                }
            )

            #..change col name
            if self.name != None:
                grouped_data.rename(columns={'value':self.name}, inplace=True)

            #..Add principal row for formatter
            grouped_data = pd.concat(
                [
                    pd.DataFrame({'name':['Laboratories']}),
                    grouped_data
                ],
                axis = 0
                ).reset_index(drop=True)
            
            logging.debug(f'Laboratories added')
            return grouped_data
        
        except Exception as e:
            raise logging.error(f'{self._createLaboratories.__name__} falied. {e}')
        
        
if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    data = pd.read_csv('./data/diabetia.csv',low_memory=False,nrows=100)
    tableone = TableOne(data=data)
    tableone.create()
    