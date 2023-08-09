"""
Auxiliar script to define normalization and standardization methods
"""

import pandas as pd
import numpy as np
import os
import logging
from sklearn.preprocessing import PowerTransformer
from sklearn.preprocessing import QuantileTransformer
from sklearn.preprocessing import StandardScaler

yeo_johnson = PowerTransformer(
    method = 'yeo-johnson',
    standardize = False
)

box_cos = PowerTransformer(
    method = 'box_cox',
    standardize = False
)

quantile_transform = QuantileTransformer(
    n_quantiles = 10000,
    output_distribution = 'normal',
    random_state = 42
)

z_score = StandardScaler(with_mean=True, with_std=True)

normalizers:dict[str:object] = {
    'yeo_johnson': yeo_johnson,
    'box_cox': box_cos,
    'quantile_transform': quantile_transform    
} 

scalers:dict[str:object] = {
    'z_score':z_score
}