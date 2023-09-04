from sklearn.neural_network import MLPClassifier

mlpc_256 = MLPClassifier(
    hidden_layer_sizes=(256,128,64,)
)