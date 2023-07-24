import sys
sys.path.append('/Users/joaquintripp/Documents/GitHub/diabetia/sc-joaquin/hta/ML_database')

import pandas as pd
import numpy as np
import re
import os
import json
from __tables__ import * 
from math import ceil
from math import floor

class Read:

    def __init__(
        self,
        folder:str,
        outFolder:str
        ):
        self.config = json.load(open(f'{os.path.dirname(__file__)}/config.json'))['PATHS']
        self.mainPath = self.config['mainPath']
        self.outPath = f"{self.config['outPath']}/{folder}"
        self.outTbl = f"{self.config['outTable1']}/{outFolder}"
        self.rows = None


    def run(self):
        tbl_patients = pd.read_csv(f'{self.outPath}/registers.csv', low_memory=False,nrows=self.rows)
        tbl_consulta = pd.read_csv(f'{self.mainPath}/ready/corhis_consulta.csv', low_memory=False, nrows=self.rows)
        tbl_diag = pd.read_csv(f'{self.mainPath}/ready/exprel_diag.csv', low_memory=False, nrows=self.rows)
        tbl_soma = pd.read_csv(f'{self.mainPath}/ready/corhis_somatometria.csv', low_memory=False,nrows=self.rows)
        tbl_receta = pd.read_csv(f'{self.mainPath}/ready/receta_med.csv', low_memory=False,nrows=self.rows)
        tbl_diabetes = pd.read_csv(f'{self.mainPath}/exphis_diabetes.csv',low_memory=False,nrows= self.rows)
        
        tables = {
        'tbl_patients':tbl_patients,
        'tbl_consulta':tbl_consulta,
        'tbl_diag':tbl_diag,
        'tbl_soma':tbl_soma,
        'tbl_receta':tbl_receta,
        'tbl_diabetes':tbl_diabetes
         }
    
        for k,v in tables.items():
            print(k,v.shape)
        print('Tables has been loaded')

        return tables



if __name__ == '__main__':
    read = Read()
    tables = read.run()
    locals().update(**tables)
    del tables
    print(locals())
