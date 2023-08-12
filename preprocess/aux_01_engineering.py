# Import libraries
import pandas as pd
import numpy as np
import re
import os
import json
import sys
from sklearn import preprocessing
from alive_progress import alive_bar
ROOT_PATH:str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.logging import logging


#############################################################################
# Auxiliar functions
#############################################################################
def snakeCase(string:str) -> str:
    """
    Function to change a string into snake case
    """
    string = str(string)
    replaces = {
        'á':'a',
        'é':'e',
        'í':'i',
        'ó':'o',
        'ú':'u',
        'ñ':'n',
        ' ':'_',
        ',':'',
        '.':'',
        '[':'',
        ']':'',
        '-':'_'
    }
    
    string = string.split()
    string = [s.strip().lower() for s in string]
    string = '_'.join(string)
        
    for k,v in replaces.items():
        string = string.replace(k,v)
    
    return string
#############################################################################   



class CleanFunctions:   
    def translateColumns(self):
        """
        Function to translate spanish Columns into english. To consult this translation go to config.json file
        """
        try:
            #..translation dictionary
            translation:dict = self.config['columnNamesTranslation']
            self.data.columns = [translation.get(name,'error') for name in self.data.columns]
            logging.info(f'Columns translated into english')
        except Exception as e:
            raise logging.error(f'{self.translateColumns.__name__} failed. {e}')
    

    def cleanHeaders(self):
        """
        function to clean headers and json file
        """    
        try:
            #..updating names in file
            self.data.columns = [snakeCase(str(column)) for column in self.data.columns]
            return logging.info('Headers converted into snakeCase')
        except Exception as e:
            raise logging.error(f'{self.cleanHeaders.__name__} failed. {e}')

    def cleanCareunit(self):
        """
        Function to clean careunit and transform it into onehot
        """
        try:
            #....one hot for cd_hallazgo
            auxOneHot: pd.DataFrame = pd.get_dummies(self.data['careunit'])
            auxOneHot.columns = [ snakeCase(col) for col in auxOneHot.columns]
            careunit_index:int = self.data.columns.get_loc('careunit')
            self.data.drop(columns=['careunit'],inplace=True)

            #..sort cols
            for idx, col in enumerate(auxOneHot.columns):
                self.data.insert(careunit_index + idx, col, auxOneHot[col])

            logging.info(f'Careunit transformed into oneHot')
        except Exception as e:
            raise logging.error(f'{self.cleanCareunit.__name__} failed. {e}')


    def categoricalCols(self):
        """
        Function to clean categorical columns. It is required to write in engineering_conf
        the columns which are consider as categorical. For this columns will be transformed into
        labels with LabelEnconder from sklearn.
        """
        try:
            #..Get categorical cols from json config and encoder from sklearn
            categoricalCols:list[str] = self.config['config']['categorical_cols']
            encoder:object = preprocessing.LabelEncoder()
            
            #..Loop all columns in config
            for col in categoricalCols:
                self.data[col] = encoder.fit_transform(self.data[col])
                
            return logging.info('Categorical cols transformed')
        
        except Exception as e:
            raise logging.error(f'{self.categoricalCols.__name__} failed. {e}')
        

    def ordinalCols(self):
        """
        Function to clean ordinal columns. It is required to write in engineering_conf
        the columns which are consider as ordinal. 
        """
        try:
            #..Get ordinal cols from json config file
            ordinalCols:list[str] = self.config['config']['ordinal_cols']

            #..Loop all columns in config
            for column in ordinalCols:
                self.data[column] = \
                    pd.to_datetime(self.data[column], errors='coerce')\
                    .apply(lambda x: x.toordinal() if pd.isnull(x) == False else x)
                
            return logging.info('Ordinal cols transformed')
        except Exception as e:
            raise logging.error(f'{self.ordinalCols.__name__} failed. {e}') 
        
class CreateFunctions:
    def createYearSinceDx(self):
        """
        Function to update anio_dx for year since T2D diagnosis
        """
        try:
            yearsSinceDx = pd.to_datetime(self.data['x_start']).dt.year
            self.data.insert(3,'years_since_dx', yearsSinceDx)
            self.data['years_since_dx'] = self.data.apply(lambda x: x['years_since_dx']-x['anio_dx'] if x['anio_dx'] > 0  else 0,axis=1)
            self.data.loc[(self.data[self.data['years_since_dx']<0]).index,'years_since_dx'] = 0
            return logging.info('Year since Dx updated')
        except Exception as e:
            raise logging.error(f'{self.createYearSinceDx.__name__} failed. {e}')
        

    def createAgeDx(self):
        """
        Function to calculate age at T2D diagnosis
        """
        try:
            aux = self.data[['id','birthdate','anio_dx']].sort_values(by=['id','birthdate'], ascending = True)
            aux = aux[aux['anio_dx'].isnull()==False]
            aux = aux.drop_duplicates(subset='id', keep = 'first')
            aux['birthdate'] = pd.to_datetime(aux['birthdate']).dt.year
            aux['age_diag'] = aux['anio_dx'] - aux['birthdate']
            aux_ages:dict = dict(zip(aux['id'],aux['age_diag']))
            self.data.insert(4,'age_diag', self.data['id'].apply(lambda x: aux_ages.get(x,np.nan)))
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
            categories:dict = {
                '18-44':[18,44],
                '45-64':[45,64],
                '65>':[65,120]
            }
            age_diag_index:int = self.data.columns.get_loc('age_diag')
            self.data.insert(age_diag_index+1,'age_diag_cat',np.nan)
            for cat,values in categories.items():
                self.data.loc[
                    (
                        self.data[
                                (self.data['age_diag']>=values[0]) &\
                                (self.data['age_diag']<=values[1])
                            ]
                    ).index,
                    'age_diag_cat'
                    ] = cat

            logging.info(f'Age at T2D Dx group added')

        except Exception as e:
            raise logging.error(f'{self.createAgeDxGroup.__name__} failed. {e}')
        

    def createBmiCategory(self):
        """
        Function to add BMI categories
        """
        try:
            targetCol:str = 'fn_weight_median'
            col_index:int = self.data.columns.get_loc(targetCol)
            self.data.insert(col_index,'bmi',np.nan)
            self.data.insert(col_index+1,'bmi_label',np.nan)


            self.data.loc[(self.data[(self.data['fn_weight_median']>0)&(self.data['fn_height_median']>0)]).index,'bmi'] = \
                self.data.loc[(self.data[(self.data['fn_weight_median']>0)&(self.data['fn_height_median']>0)]).index,['fn_weight_median','fn_height_median']].apply(lambda x: x['fn_weight_median'] / (x['fn_height_median']**2), axis=1)

            self.data['bmi_label'] = pd.cut(
                 self.data['bmi'],
                bins = [0,18.5,25,30,35,40,150],
                right = False,
                labels = ['Underweight','Normal weight','Pre-obesity','Obesity (class 1)','Obesity (class 2)','Obesity (class 3)']
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
            targetCols:list[str] = [
                'in_glucose_median',
                'fn_fasting_glucose_median',
                'fn_capillary_glucose_median',
                'fn_glycemia_median'
                ]
            
            #..Insert new cols in index
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index, 'glucose_total', self.data[targetCols[0]])
            self.data.insert(col_index+1, 'glucose_label', np.nan)

            #..glucose imputation
            self.data.loc[
                (self.data[
                    (self.data['glucose_total'].isnull())\
                    & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                    ]).index,
                'glucose_total'
                ] = self.data.loc[
                    (self.data[
                        (self.data['glucose_total'].isnull())\
                        & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                        ]).index,
                    targetCols[1:]
                    ].mean(axis=1)
            
            #..Build label var
            self.data['glucose_label'] = pd.cut(
                self.data['glucose_total'],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Glucose categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createGlucoseCategory.__name__} failed. {e}')
        

    def createHemoglobinCategory(self):
        """
        man:
        <6
        6-8
        8-10
        10-12
        12-16
        16>
        """
        try:
            logging.info('Hemoglobin categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createHemoglobinCategory.__name__} failed. {e}')
        
    
    def createTriglyceridesCategory(self):
        try:
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
            logging.info('Creatinine categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createCreatinineCategory.__name__} failed. {e}')
        

    def createCholesterolCategory(self):
        try:
            logging.info('Cholesterol categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createCholesterolCategory.__name__} failed. {e}')
     
    
    

        
        
    def __str__(self):
        return 'Data engineering functions'


class UpdateFunctions:
    def updateDiagnosis(self): 
        """
        Function to change the Y variables into multilabel vars depending on the case it represents
        (Y vars are include also in X vars). 
        The cases are classified as follow:
        Considering [X,Y]:
        1. [0,0] = 0
        2. [0,1] = 1
        3. [1,1] = 2
        """  
        try:
            #..Get diagnosis columns from json config file
            dxCols:dict[str:str] = self.config['config']['diagnosis']

            #..Loop through dxCols dictionary to clean each dx
            with alive_bar(len(dxCols.keys()), title='### Y Values in transformation') as bar:
                for cie, name in dxCols.items():
                    self.data.loc[(self.data[(self.data[name] == 0) & (self.data[cie]==0)]).index,cie] = 0
                    self.data.loc[(self.data[(self.data[name] == 0) & (self.data[cie]==1)]).index,cie] = 1
                    self.data.loc[(self.data[(self.data[name] == 1) & (self.data[cie]==1)]).index,cie] = 2
                    bar()
            return logging.info(f'Y Values transformed into labels')
        except Exception as e:
            raise logging.error(f'Y Values were not transformed. {e}')


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
            raise logging.error(f'Columns were not dropped. {e}')