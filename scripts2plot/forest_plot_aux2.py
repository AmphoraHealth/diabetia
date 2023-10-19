""" 
forest_plot_aux.py
    This file generates forest plot of Relative Risk and Odds ratio of all DM2 complications

Input:
  - data/supplementary_material/data_aux/{effect_file}.csv
Output:
  - Effects.png

"""

# Environment preparation
import os
import sys

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.logging import logging


# Constant definition
OUT_PATH_IMG = 'data/supplementary_material/visualizations'
INPUT_PATH_DATA = 'data/supplementary_material/data_aux'
CONFIG_PATH = './conf/engineering_conf.json'


#Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import json

#Default config
warnings.filterwarnings("ignore")
definitions = json.load(open(f'{CONFIG_PATH}', 'r', encoding='UTF-8'))['config']['diagnosis']


def generate_plot(relativerisks:pd.DataFrame, oddsratios:pd.DataFrame, plot_name:str, top:int = 5, tail:int = 5, reference_value:int = 1, ascending:bool = False, logscale:bool = False, figsize:tuple = (20,60)):
    """
    Function to generate a forest plot from an risk effect estimation
    """
    complications = ['Nephropathy', 'Retinopathy', 'Neuropathy', 'Diabetic foot']
    fig, axs = plt.subplots(2, 2, figsize=figsize, sharex = True)
    # i = 0
    # for df in relativerisks:
    #     if ascending:
    #         df.sort_values(by = 'RelativeRisk', ascending = False, inplace = True)
    #     else:
    #         df.sort_values(by = 'RelativeRisk', ascending = True, inplace = True)
    #     df = df[(df['RelativeRisk']>0) & (df['RelativeRisk']<float('inf'))]

    #     df1 = df[df['Lower'] > 1.3]
    #     df2 = df[df['Upper'] < 0.85]
        
    #     df = pd.concat([df2.head(tail), df1.tail(top)])
            
    #     x_err_low = [list(df['RelativeRisk'])[i] - list(df['Lower'])[i] for i in range(len(df))]
    #     x_err_high = [list(df['Upper'])[i] - list(df['RelativeRisk'])[i] for i in range(len(df))]

    #     axs[i,0].errorbar(list(df['RelativeRisk']), np.arange(len(df)), xerr=[x_err_low, x_err_high], fmt='.', color='gray', capsize=5, label='Confidence Interval', zorder=0)
    #     axs[i,0].scatter(list(df['RelativeRisk']), np.arange(len(df)), color='black',marker='s', label='Effect', zorder=10)
    #     axs[i,0].axvline(x=reference_value, color='red', linestyle='--', label='Reference', alpha = 0.6)
    
    #     summary_variables = []
    #     for v in list(df['Variable']):
    #         v_aux = v.split(' ')
    #         if 'infarction' in v_aux:
    #             v_aux = 'complications after acute myocardial infarction'
    #             summary_variables.append(v_aux)
    #         else:
    #             if len(v_aux) > 5:
    #                 if v_aux[4] == 'and' or v_aux[4] == 'of':
    #                     v_aux = ' '.join(v_aux[:4])
    #                 else:
    #                     v_aux = ' '.join(v_aux[:6])

    #             else:
    #                 v_aux = ' '.join(v_aux)
    #             v_aux = v_aux.replace(' as', '')
    #             summary_variables.append(v_aux)
        
    #     axs[i,0].set_yticks(np.arange(len(df)), summary_variables)
    #     axs[i,0].grid(axis='x', linestyle='--', alpha=0.8)
    #     axs[i,0].grid(axis='y', linestyle='--', alpha=0.8)
    #     if logscale == True:
    #         axs[i,0].set_xscale('log')
    #     axs[i,0].tick_params(axis='y', which='major', labelsize=12)
    #     axs[i,0].tick_params(axis='x', which='major', labelsize=13)
        
    #     axs[i,0].set_ylabel(complications[i], fontsize = 19, labelpad=5)
    #     axs[i,0].get_yaxis().set_label_coords(-0.7,0.5)
        
    #     if i == 0:
    #         axs[i,0].set_title('Relative Risk', fontsize = 20)
        
    #     i += 1
        
    i,j,k = 0, 0, 0
    for df in oddsratios:
        if ascending:
            df.sort_values(by = 'OddsRatio', ascending = False, inplace = True)
        else:
            df.sort_values(by = 'OddsRatio', ascending = True, inplace = True)
        
        df = df[(df['OddsRatio']>0) & (df['OddsRatio']<float('inf'))]

        # df = df[abs(df['Upper'] - df['Lower']) <= 100]

        # df1 = df[df['Lower'] > 1.3]
        # df2 = df[df['Upper'] < 0.85]
        # df = pd.concat([df2.head(tail), df1.tail(top)])
            
        x_err_low = [list(df['OddsRatio'])[i] - list(df['Lower'])[i] for i in range(len(df))]
        x_err_high = [list(df['Upper'])[i] - list(df['OddsRatio'])[i] for i in range(len(df))]

        axs[i,j].errorbar(list(df['OddsRatio']), np.arange(len(df)), xerr=[x_err_low, x_err_high], fmt='.', color='gray', capsize=5, label='Confidence Interval', zorder=0)
        axs[i,j].scatter(list(df['OddsRatio']), np.arange(len(df)), color='black',marker='s', label='Effect', zorder=10)
        axs[i,j].axvline(x=reference_value, color='red', linestyle='--', label='Reference', alpha = 0.6)

        summary_variables = []
        for v in list(df['Variable']):
            v_aux = v.split(' ')
            if 'infarction' in v_aux:
                v_aux = 'complications after acute myocardial infarction'
                summary_variables.append(v_aux)
            else:
                if len(v_aux) > 5:
                    if v_aux[4] == 'and' or v_aux[4] == 'of':
                        v_aux = ' '.join(v_aux[:4])
                    else:
                        v_aux = ' '.join(v_aux[:6])

                else:
                    v_aux = ' '.join(v_aux)
                v_aux = v_aux.replace(' as', '')
                summary_variables.append(v_aux)
        axs[i,j].set_yticks(np.arange(len(df)), summary_variables)
        axs[i,j].grid(axis='x', linestyle='--', alpha=0.8)
        axs[i,j].grid(axis='y', linestyle='--', alpha=0.8)
        if logscale == True:
            axs[i,j].set_xscale('log')
        axs[i,j].tick_params(axis='y', which='major', labelsize=12)
        axs[i,j].tick_params(axis='x', which='major', labelsize=13)
        axs[i,j].set_ylabel(complications[k], fontsize = 17, labelpad=7)
        
        if j < 1:
            j = j+1
        else:
            i = i+1
            j = 0

        k = k+1

        # if i == 0:
        #     axs[i,1].set_title('Odds Ratio', fontsize = 20)
        
        # i += 1
    
    current_handles, current_labels = plt.gca().get_legend_handles_labels()
    fig.suptitle('Odds Ratio Analysis', fontsize = 23, y=1.005)
    fig.legend(current_handles, current_labels, loc='lower center', ncol = 3, bbox_to_anchor=(0.55, -0.04), borderaxespad=0, fontsize=15)
    
    plt.tight_layout()
    plt.savefig(f'{OUT_PATH_IMG}/{plot_name + ".jpg"}', bbox_inches="tight", dpi = 600)


def main():
    try:
        or_e112 = pd.read_csv(f'{INPUT_PATH_DATA}/OddsRatio_e112.csv')
        or_e113 = pd.read_csv(f'{INPUT_PATH_DATA}/OddsRatio_e113.csv')
        or_e114 = pd.read_csv(f'{INPUT_PATH_DATA}/OddsRatio_e114.csv')
        or_e115 = pd.read_csv(f'{INPUT_PATH_DATA}/OddsRatio_e115.csv')
        rr_e112 = pd.read_csv(f'{INPUT_PATH_DATA}/RelativeRisk_e112.csv')
        rr_e113 = pd.read_csv(f'{INPUT_PATH_DATA}/RelativeRisk_e113.csv')
        rr_e114 = pd.read_csv(f'{INPUT_PATH_DATA}/RelativeRisk_e114.csv')
        rr_e115 = pd.read_csv(f'{INPUT_PATH_DATA}/RelativeRisk_e115.csv')
    except:
        logging.error('Effect file missing')

    or_effects = [or_e112, or_e113, or_e114, or_e115]
    rr_effects = [rr_e112, rr_e113, rr_e114, rr_e115]

    generate_plot(rr_effects, or_effects, 'Effect_ForestPlot', logscale = True, figsize = (21,10))

    

if __name__ == "__main__":
    main()