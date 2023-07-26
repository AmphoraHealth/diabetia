import pandas as pd
import numpy as np
import re
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json
from tableone import TableOne
from math import floor,ceil
from scipy.stats import chi2
from itertools import combinations

import warnings
warnings.filterwarnings('ignore')


# add code constants
CONFIG = json.load(open(f'{os.path.dirname(__file__)}/config.json','r'))
IN_PATH = f"{os.getcwd()}/data/diabetia.csv"
OUT_PATH = f"{os.getcwd()}/data/table_one"

class TableConstruction:

    def __init__(
        self,
        fileName:str,
        dataPath:str,
        outPath:str
        ):

        self.localPath:str = os.path.dirname(__file__)
        self.config = json.load(open(f'{self.localPath}/config.json','r'))
        self.dataPath = dataPath
        self.outPath = outPath
        self.pt:pd.DataFrame = pd.read_csv(fileName)
        self.cols:dict = self.config['COLUMNS']


    def chi_squared(self,total1,total2,value1,value2):
    
        try:
            k11 = int(value1)
            k12 = int(value2)
            k21 = total1-int(value1)
            k22 = total2-int(value2)

            rtotal1 = k11+k12
            rtotal2 = k21+k22

            total = total1+total2

            k11p = (total1*rtotal1)/ total
            k12p = (total2*rtotal1)/ total
            k21p = (total1*rtotal2)/ total
            k22p = (total2*rtotal2)/ total

            result = \
                (((k11-k11p)**2)/k11p)\
                + (((k12-k12p)**2)/k12p)\
                + (((k21-k21p)**2)/k21p)\
                + (((k22-k22p)**2)/k22p)

            return chi2.sf(result,1)
        except:
            return np.nan
    

    def addOR(self,total1,total2,value1,value2):

        try:
            k11 = int(value1)
            k12 = int(value2)
            k21 = total1-int(value1)
            k22 = total2-int(value2)
            
            odds = (k11/k21)/(k12/k22)
            return odds
        except:
            return np.nan
        

    def addCI(self,total1,total2,value1,value2):
        
        odds = self.addOR(total1,total2,value1,value2)

        try:
            k11 = int(value1)
            k12 = int(value2)
            k21 = total1-int(value1)
            k22 = total2-int(value2)
            
            se = np.sqrt((1/k11)+(1/k21)+(1/k12)+(1/k22))
            ci1 = round(np.exp(np.log(odds)-1.96*se),4)
            ci2 = round(np.exp(np.log(odds)+1.96*se),4)
            
            return [ci1,ci2]
        except:
            return np.nan


    def run(self):
        """
        Process to read summarized file of diabetes registers and build table one
        """
        columns = [n for n in self.pt.columns if n not in self.cols['colsCancer']+self.cols['colsInfo']]
        age_columns = ['age_diag','age_index']


        #....Table one groupby condition (OVERALL, HTN_WH_T2D, T2D_WH_HTN, TD2_W_HTN, NONE)
        pt_1 = TableOne(
                data = self.pt, 
                categorical = columns , 
                columns = columns ,
                pval = False, 
                pval_adjust=False, 
                overall = True, 
                label_suffix = True, 
                row_percent = False,
                groupby = 'condition'
        )

        #....Table one for W_T2D
        pt_2 = TableOne(
                data = self.pt, 
                categorical = columns , 
                columns = columns ,
                pval = False, 
                pval_adjust=False, 
                overall = True, 
                label_suffix = True, 
                row_percent = False,
                groupby = 'T2D'
        )

        # CONCATENATE OVERALL AND T2D TABLES
        """
        For this step, is required to save and read again tables to convert into pandas format.
        Both files are concatenated in order to have all groups together
        """

        if not os.path.exists(self.outPath):
            os.system(f'mkdir {self.outPath}')

        pt_1.to_csv(f'{self.outPath}/OVERALL.csv', encoding = 'Utf-8', sep=',')
        pt_2.to_csv(f'{self.outPath}/W_T2D.csv', encoding = 'Utf-8', sep=',')

        #..Process to overall (OVERALL T2D_WH_HTN, T2D_W_HTN, HTN_WH_T2D,NONE)
        pt_ov = pd.read_csv(f'{self.outPath}/OVERALL.csv',low_memory=True)
        pt_ov.columns = ['Variables','Levels']+[n for n in list(pt_ov.iloc[0:1,:].values[0]) if str(n) != 'nan']

        pt_ov = pt_ov[pt_ov['Levels']!='0']
        pt_ov.drop(pt_ov.iloc[0:1,:].index,inplace=True)
        pt_ov.set_index(['Variables','Levels'],inplace=True)

        #..Process to W_T2D and WH_T2D
        pt_diab = pd.read_csv(f'{self.outPath}/W_T2D.csv',low_memory=True)
        pt_diab.columns = ['Variables','Levels']+[n for n in list(pt_diab.iloc[0:1,:].values[0]) if str(n) != 'nan']
        pt_diab.drop(columns=['Missing','Overall'],inplace=True)
        pt_diab.rename(columns = {'0':'WH_T2D','1':'W_T2D'},inplace=True)

        pt_diab = pt_diab[pt_diab['Levels']!='0']
        pt_diab.drop(pt_diab.iloc[0:1,:].index,inplace=True)
        pt_diab.set_index(['Variables','Levels'],inplace=True)

        #..CONCATENATE
        print(pt_ov)
        print(pt_diab)
        pt_all = pd.concat([pt_ov,pt_diab],axis=1)

        ###########################################################################################
        """
        pt_all has only diagnosis, sex and BMI categories. With next process Age at index and age
        at dx are added.
        """
        # AGE INDEX AND AGE DX
        #..Age at index

        age_1 = pd.concat([
        self.pt[['age_index']].agg([np.mean,np.median,np.std,'count']).round(2).rename(columns={'age_index':'Overall'}),
        self.pt.groupby('condition')['age_index'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={'T2D':'T2D_WH_HTN'}),
        self.pt.groupby('T2D')['age_index'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={0:'WH_T2D',1:'W_T2D'})
        ],axis=1)[['Overall','W_T2D','T2D_WH_HTN','T2D_W_HTN','WH_T2D']]

        age_1 = age_1.set_index([['Age at index']*4,list(age_1.index)])
        age_1 = age_1.rename_axis(['Variables','Levels'])

        #..Age at diagnosis
        age_2 = pd.concat([
            self.pt[['age_diag']].agg([np.mean,np.median,np.std,'count']).round(2).rename(columns={'age_diag':'Overall'}),
            self.pt.groupby('condition')['age_diag'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={'T2D':'T2D_WH_HTN'}),
            self.pt.groupby('T2D')['age_diag'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={0:'WH_T2D',1:'W_T2D'})
        ],axis=1)[['Overall','W_T2D','T2D_WH_HTN','T2D_W_HTN','WH_T2D']]

        age_2 = age_2.set_index([['Age at Dx']*4,list(age_2.index)])
        age_2 = age_2.rename_axis(['Variables','Levels'])

        age = pd.concat([age_1,age_2])

        # CONCATENATE TABLE ONE
        #..Final
        ptOne = pd.concat([age,pt_all],axis=0)

        #..Order
        colsOrder = ['Overall','W_T2D','T2D_WH_HTN','T2D_W_HTN','WH_T2D']
        ptOne = ptOne[colsOrder]

        #..splitting
        for n in colsOrder:
            ptOne[f'({n})'] = ptOne[n].apply(lambda x: float(str(x).split(' ')[0]) if str(x) not in ['None','nan'] else np.nan) 

        # CHI2, P-VALUE AND OR
        c = combinations(['W_T2D','Overall','T2D_W_HTN','T2D_WH_HTN','WH_T2D'],2)
        print(f'{"="*30}Adding CHI2{"="*30}')
        for n in c:
            total1 = float(ptOne.loc['n',f'({n[0]})'].values[0]) 
            total2 = float(ptOne.loc['n',f'({n[1]})'].values[0]) 
            colName = f'CHI2 {n[0]}|{n[1]}'
            print(n[0],' vs ',n[1],total1,total2)
            ptOne[colName] = ptOne.iloc[9:,:].apply(lambda x: self.chi_squared(total1,total2,x[f'({n[0]})'],x[f'({n[1]})']),axis=1).astype(float).round(8)

            
        c = combinations(['W_T2D','Overall','T2D_W_HTN','T2D_WH_HTN','WH_T2D'],2)
        print(f'{"="*30}Adding OR{"="*30}')
        for n in c:
            total1 = float(ptOne.loc['n',f'({n[0]})'].values[0]) 
            total2 = float(ptOne.loc['n',f'({n[1]})'].values[0]) 
            colName = f'OR {n[0]}|{n[1]}'
            print(n[0],' vs ',n[1],total1,total2)
            ptOne[colName] = ptOne.iloc[9:,:].apply(lambda x: self.addOR(total1,total2,x[f'({n[0]})'],x[f'({n[1]})']),axis=1).astype(float).round(8)


        c = [['W_T2D','Overall'],['T2D_W_HTN','W_T2D'],['T2D_W_HTN','T2D_WH_HTN']]
        print(f'{"="*30}Adding CI{"="*30}')
        for n in c:
            total1 = float(ptOne.loc['n',f'({n[0]})'].values[0]) 
            total2 = float(ptOne.loc['n',f'({n[1]})'].values[0]) 
            colName = f'CI {n[0]}|{n[1]}'
            print(n[0],' vs ',n[1],total1,total2)
            ptOne[colName] = ptOne.iloc[9:,:].apply(lambda x: self.addCI(total1,total2,x[f'({n[0]})'],x[f'({n[1]})']),axis=1)
        
        # SAVING TABLE 1
        finalPath = f'{self.outPath}/tbl1.csv'
        if os.path.exists(finalPath):
            if input('Overwrite?[y/n]: ').lower() == 'y':
                ptOne.to_csv(finalPath)
                ptOne.to_excel(f'{self.outPath}/tbl1.xlsx')
                print(f'{"="*30} SAVED! {"="*30}')
            else:
                print('Not saved!')
        else:
            ptOne.to_csv(finalPath)
            ptOne.to_excel(f'{self.outPath}/tbl1.xlsx')
            print(f'{"="*30} SAVED! {"="*30}')

        return self.pt


def run():
    # get the final path
    userInputDataFolder = "/".join(IN_PATH.split("/")[:-1])
    userInputFile = IN_PATH
    userInputOutFolder = OUT_PATH

    # confirm the path existance
    if not os.path.exists(userInputDataFolder):
        print(f"Path {userInputDataFolder} does not exist!")
        raise Exception(f"Path {userInputDataFolder} does not exist!")
    if not os.path.exists(userInputFile):
        print(f"File {userInputFile} does not exist!")
        raise Exception(f"File {userInputFile} does not exist!")
    if not os.path.exists(userInputOutFolder):
        os.system(f"mkdir {userInputOutFolder}")

    # preprocesing

    # run the table one construction
    tblOne = TableConstruction(
        fileName=userInputFile,
        dataPath=userInputDataFolder,
        outPath=userInputOutFolder
        )

    tblOne.run()
    return

if __name__ == '__main__':
    run()