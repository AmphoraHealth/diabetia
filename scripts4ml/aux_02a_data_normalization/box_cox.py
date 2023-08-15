from sklearn.preprocessing import PowerTransformer

box_cox = PowerTransformer(
    method = 'box_cox',
    standardize = False
)