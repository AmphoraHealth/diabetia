# Import libraries
import numpy as np
import os
import sys
ROOT_PATH:str = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
    )
)
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


def calculateGFR(
        factors:dict,
        sex:str,
        age:int,
        creatinine:float
        ) -> float:
    """
    Function to calculate estimated glomerular filtration rate (eGFR).
    Input:
    - factors: factor by sex. Located in engieneering_config.json file
    - sex: "female" or "male"
    - age: int value
    - creatinine: float value. Bewteen 0.2 to 20

    Output:
    - eGFR: int value

    This funtion was guided by the equation from: Pottel H. Cystatin C-Based Equation to 
    Estimate GFR without the Inclusion of Race and Sex. N Engl J Med.
    2023 Jan 26;388(4):333-343. doi: 10.1056/NEJMoa2203769. PMID: 36720134.
    """
    try: 
        sexFactor = factors[sex]['sexFactor']
        alpha = factors[sex]['alpha']
        kappa = factors[sex]['kappa']

        GFR = \
            142 * (np.min([creatinine/kappa,1])**alpha) * (np.max([creatinine/kappa,1])**-1.2) * (0.9938**age) * sexFactor
    
        return GFR
    except Exception as e:
        raise logging.warning(f'Calculation of eGFR failed. {e}')
