from sklearn.feature_selection import chi2
import pandas as pd

class Xi2FeatureSelection:
    def fit(data, label, n_features):
        cols = [col for col in data.columns if data[col].min() < 0]
        # add the minimum value to each column to make them all positive
        data[cols] = data[cols] + abs(data[cols].min())
        # get the best features
        best_features = {}
        chi, p_vals = chi2(data, label)
        statistics = pd.DataFrame(zip(data.columns, chi, p_vals), columns = ['id', 'chi2', 'p-val']).sort_values('p-val')
        statistics = statistics.head(n_features)
        best_features['columns'] = list(statistics['id'])
        best_features['chi2'] = list(statistics['chi2'])
        best_features['p_val'] = list(statistics['p-val'])
        
        return best_features