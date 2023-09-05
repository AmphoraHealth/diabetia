import pandas as pd

_features:list[str] = [
  "birthdate",
  "years_since_dx",
  "cs_sex",
  "hgz_con_mf_no_12",
  "hgz_con_mf_no_2",
  "umf_no_75",
  "umf_no_76",
  "umf_no_77",
  "umf_no_80",
  "count_cx_w",
  "age_at_wx",
  "age_at_wx_ordinal",
  "dx_age_e11", 
  "dx_age_e11_ordinal",
  "diabetes_mellitus_type_2",
  "essential_(primary)_hypertension",
]

class Demographic:
    """This features were selected by a clinical expert"""
    def fit(data:pd.DataFrame, label, n_features):
        # get the best features
        best_features = {}
        best_features['columns'] = _features
        return best_features