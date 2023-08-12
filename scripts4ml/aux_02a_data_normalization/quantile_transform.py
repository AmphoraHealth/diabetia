from sklearn.preprocessing import QuantileTransformer

quantile_transform = QuantileTransformer(
    n_quantiles = 10000,
    output_distribution = 'normal',
    random_state = 42
)