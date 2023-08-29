from sklearn.naive_bayes import GaussianNB
from sklearn.feature_selection import SequentialFeatureSelector

class ProbabilisticForwardSelection:
    def fit(data:pd.DataFrame, label:pd.Series, n_features:int):
        best_features = {}
        naive_bayes = GaussianNB()
        forward_selection = SequentialFeatureSelector(naive_bayes, n_features_to_select=n_features, direction="forward")
        forward_selection.fit(data, label)
        best_features['columns'] = list(data.columns[forward_selection.get_support()])

        return best_features