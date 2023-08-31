import pandas as pd

class DummyFeatureSelection:
    def fit(data:pd.DataFrame, label:pd.Series, n_features:int):
        best_features = {}
        best_features['columns'] = list(data.columns)
        return best_features