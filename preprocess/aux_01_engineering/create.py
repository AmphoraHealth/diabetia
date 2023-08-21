# Import libraries
import pandas as pd
import numpy as np
import os
import sys
from math import ceil
from aux_01_engineering.aux_functions import calculateGFR

ROOT_PATH:str = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging


class CreateFunctions:
    def createYearSinceDx(self):
        """
        Function to update dx_year_e11 for year since T2D diagnosis
        """
        try:
            yearsSinceDx = pd.to_datetime(self.data['x_start']).dt.year
            self.data.insert(3,'years_since_dx', yearsSinceDx)
            self.data['years_since_dx'] = self.data.apply(lambda x: x['years_since_dx']-x['dx_year_e11'] if x['dx_year_e11'] > 0  else 0,axis=1)
            self.data.loc[(self.data[self.data['years_since_dx']<0]).index,'years_since_dx'] = 0
            return logging.info('Year since Dx updated')
        except Exception as e:
            raise logging.error(f'{self.createYearSinceDx.__name__} failed. {e}')
        

    def createAgeDx(self):
        """
        Function to calculate age at T2D diagnosis
        """
        try:
            #..auxiliar frame to calculate age at first T2D diagnosis
            aux = self.data[['id','birthdate','dx_year_e11']].sort_values(by=['id','birthdate'], ascending = True)
            aux = aux[aux['dx_year_e11'].isnull()==False]
            aux = aux.drop_duplicates(subset='id', keep = 'first')
            aux['birthdate'] = pd.to_datetime(aux['birthdate']).dt.year
            aux['dx_age_e11'] = aux['dx_year_e11'] - aux['birthdate']
            aux_ages:dict = dict(zip(aux['id'],aux['dx_age_e11']))

            #..mapping ages by cx_curp
            self.data.insert(4,'dx_age_e11', self.data['id'].apply(lambda x: aux_ages.get(x,np.nan)))

            return logging.info('Age at Dx created')
        except Exception as e:
            raise logging.error(f'{self.createAgeDx.__name__} failed. {e}')


    def createAgeDxGroup(self):
        """
        Function to stablish categories for Age at T2D diagnosis: 
        18 - 44
        45 - 64
        65 >
        """
        try:
            #..setting default vales
            categories:dict = self.config['ageAtDxConfig']['categories']
            dx_age_e11_index:int = self.data.columns.get_loc('dx_age_e11')
            self.data.insert(dx_age_e11_index+1,'dx_age_e11_cat',np.nan)
            for cat,values in categories.items():
                self.data.loc[
                    (
                        self.data[
                                (self.data['dx_age_e11']>=values[0]) &\
                                (self.data['dx_age_e11']<=values[1])
                            ]
                    ).index,
                    'dx_age_e11_cat'
                    ] = cat

            logging.info(f'Age at T2D Dx group added')

        except Exception as e:
            raise logging.error(f'{self.createAgeDxGroup.__name__} failed. {e}')
        

    def createBmiCategory(self):
        """
        Function to add BMI categories
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']["bmi"]['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']["bmi"]['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['bmi']['targetCols']
            valueColName:str = self.config['categoricalMeasuresConfig']["bmi"]['valueCol']
            labelColName:str = self.config['categoricalMeasuresConfig']["bmi"]['labelCol']
            weight:str = targetCols[0]
            height:str = targetCols[1]
            
            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,valueColName,np.nan)
            self.data.insert(col_index+1,labelColName,np.nan)


            self.data.loc[(self.data[(self.data[weight]>0)&(self.data[height]>0)]).index,valueColName] = \
                self.data.loc[(self.data[(self.data[weight]>0)&(self.data[height]>0)]).index,[weight,height]].apply(lambda x: x[weight] / (x[height]**2), axis=1)

            self.data[labelColName] = pd.cut(
                 self.data[valueColName],
                bins = ranges,
                right = False,
                labels = labels
            )

            logging.info('BMI categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createBmiCategory.__name__} failed. {e}')
        

    def createGlucoseCategory(self):
        """
        Function to add glucose categories. There is an imputation for glucose level:
        1. If patient has in_glucose_median = use in_glucose_median
        2. If patient does not have in_glucose_median = use mean of:
            -fn_fasting_glucose_mean,fn_capillary_glucose_mean,fn_glycemia_mean
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']["glucose"]['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']["glucose"]['labels']
            targetCols:list[str] = self.config['categoricalMeasuresConfig']['glucose']['targetCols']
            valueColName:str = self.config['categoricalMeasuresConfig']["glucose"]['valueCol']
            labelColName:str = self.config['categoricalMeasuresConfig']["glucose"]['labelCol']
            
            #..Insert new cols in index
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index, valueColName, self.data[targetCols[0]])
            self.data.insert(col_index+1, labelColName, np.nan)

            #..clean glucose under 25
            self.data.loc[
                (self.data[
                    self.data[valueColName]<25\
                    ]).index,
                valueColName
                ] = np.nan

            #..glucose imputation
            self.data.loc[
                (self.data[
                    (self.data[valueColName].isnull())\
                    & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                    ]).index,
                valueColName
                ] = self.data.loc[
                    (self.data[
                        (self.data[valueColName].isnull())\
                        & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                        ]).index,
                    targetCols[1:]
                    ].mean(axis=1)
            
            #..Build label var
            self.data[labelColName] = pd.cut(
                self.data[valueColName],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Glucose categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createGlucoseCategory.__name__} failed. {e}')
        

    def createHemoglobinCategory(self):
        """
        Function to create hemoglobin categorical col. It is a simple discretization
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['hemoglobin']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['hemoglobin']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['hemoglobin']['targetCols']
            valueColName:str = self.config['categoricalMeasuresConfig']["hemoglobin"]['valueCol']
            labelColName:str = self.config['categoricalMeasuresConfig']["hemoglobin"]['labelCol']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,valueColName,self.data[targetCols[0]])
            self.data.insert(col_index+1,labelColName, np.nan)

            #..Build label var
            self.data[labelColName] = pd.cut(
                self.data[valueColName],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Hemoglobin categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createHemoglobinCategory.__name__} failed. {e}')
        
    
    def createTriglyceridesCategory(self):
        """
        Function to create triglicerides columns. It is a simple discretization
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['triglycerides']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['triglycerides']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['triglycerides']['targetCols']
            valueColName:str = self.config['categoricalMeasuresConfig']["triglycerides"]['valueCol']
            labelColName:str = self.config['categoricalMeasuresConfig']["triglycerides"]['labelCol']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,valueColName, self.data[targetCols[0]])
            self.data.insert(col_index+1,labelColName, np.nan)

            #..Build label var
            self.data[labelColName] = pd.cut(
                self.data[valueColName],
                bins = ranges,
                labels = labels,
                right = False
                )
            
            logging.info('Triglycerides categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createTriglyceridesCategory.__name__} failed. {e}')
        

    def createDiabeticFootCategory(self):
        try:
            logging.info('Diabetic foot categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createDiabeticFootCategory.__name__} failed. {e}')
        

    def createCreatinineCategory(self):
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['creatinine']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['creatinine']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['creatinine']['targetCols']
            eGFR_Factors:dict = self.config['categoricalMeasuresConfig']['creatinine']['factors']
            valueColName:str = self.config['categoricalMeasuresConfig']["creatinine"]['valueCol']
            labelColName:str = self.config['categoricalMeasuresConfig']["creatinine"]['labelCol']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,valueColName, np.nan)
            self.data.insert(col_index+1,labelColName, np.nan)

            #..apply eGFR
            self.data.loc[
                (self.data[self.data[targetCols[0]].isnull()==False]).index,
                valueColName
            ] = self.data.loc[
                (self.data[self.data[targetCols[0]].isnull()==False]).index,
                targetCols
            ].apply(
                lambda x: calculateGFR(
                    factors = eGFR_Factors,
                    sex = x[targetCols[2]],
                    age = x[targetCols[1]],
                    creatinine = x[targetCols[0]]
                    ),
                axis = 1
                )
            
            #..Build label var
            self.data[labelColName] = pd.cut(
                self.data[valueColName],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Creatinine categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createCreatinineCategory.__name__} failed. {e}')
        

    def createCholesterolCategory(self):
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['cholesterol']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['cholesterol']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['cholesterol']['targetCols']
            valueColName:str = self.config['categoricalMeasuresConfig']["cholesterol"]['valueCol']
            labelColName:str = self.config['categoricalMeasuresConfig']["cholesterol"]['labelCol']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,valueColName, self.data[targetCols[0]])
            self.data.insert(col_index+1,labelColName, np.nan)

            #..Build label var
            self.data[labelColName] = pd.cut(
                self.data[valueColName],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Cholesterol categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createCholesterolCategory.__name__} failed. {e}')
        

    def createDiabeticFoot(self):
        """
        Funtion to create an ordinal and rounded. This column only is rounded to up,
        orginal column is ordinal, but it has some vallues with decimals in fn_..._median vars.
        """
        try:
            #..crete new col
            index_col_left:int = self.data.columns.get_loc('fn_left_foot_median')
            index_col_right:int = self.data.columns.get_loc('fn_left_foot_median')
            self.data.insert(index_col_left,'diabetic_left_foot_ordinal',self.data['fn_left_foot_median'])
            self.data.insert(index_col_right,'diabetic_right_foot_ordinal',self.data['fn_left_foot_median'])
            
            #..ceil left foot
            self.data.loc[
                (self.data[self.data['diabetic_left_foot_ordinal'].isnull()==False]).index,\
                'diabetic_left_foot_ordinal'
                ] = self.data.loc[
                    (self.data[self.data['diabetic_left_foot_ordinal'].isnull()==False]).index,\
                    'diabetic_left_foot_ordinal'
                ].apply(lambda x: ceil(x))
            
            #..ceil right foot
            self.data.loc[
                (self.data[self.data['diabetic_right_foot_ordinal'].isnull()==False]).index,\
                'diabetic_right_foot_ordinal'
                ] = self.data.loc[
                    (self.data[self.data['diabetic_right_foot_ordinal'].isnull()==False]).index,\
                    'diabetic_right_foot_ordinal'
                ].apply(lambda x: ceil(x))

            logging.info(f'Diabetic foot cols created')
        except Exception as e:
            raise logging.error(f'{self.createDiabeticFoot.__name__} failed. {e}')
        

    def __str__(self):
        return 'Data engineering functions'

