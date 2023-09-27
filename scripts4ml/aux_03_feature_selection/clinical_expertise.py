from sklearn.feature_selection import chi2
import pandas as pd

_features:list[str] = [
    'years_since_dx',
    'cs_sex',
    'age_at_wx',
    'age_at_wx_ordinal',
    'dx_age_e11',
    'dx_age_e11_ordinal',
    'bmi_value',
    'bmi_ordinal',
    'diabetes_mellitus_type_2',
    'essential_(primary)_hypertension',
    'disorders_of_lipoprotein_metabolism_and_other_lipidemias',
    'gfr_value',
    'gfr_ordinal',
    'glucose_value',
    'glucose_ordinal',
    'hemoglobin_value',
    'hemoglobin_ordinal',
    'triglycerides_value',
    'triglycerides_ordinal',
    'cholesterol_value',
    'cholesterol_ordinal',
    'type_2_diabetes_mellitus_with_renal_complications',
    'type_2_diabetes_mellitus_with_ophthalmic_complications',
    'type_2_diabetes_mellitus_with_neurological_complications',
    'type_2_diabetes_mellitus_with_peripheral_circulatory_complications'
]

class ClinicalExpertise:
    """This features were selected by a clinical expert"""
    def fit(data, label, n_features):
        # get the best features
        best_features = {}
        best_features['columns'] = _features
        return best_features