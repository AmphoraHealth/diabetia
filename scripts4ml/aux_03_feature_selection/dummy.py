import pandas as pd

class DummyFeatureSelection:
    def fit(data:pd.DataFrame, label:pd.Series, n_features:int):
        best_features = {}
        best_features['columns'] = data.columns
        return best_features