from .ada_boost import ada_boost
from .gaussian_nb import gaussian_nb
from .knc import knc
from .logistic import logistic
from .mlpc import mlpc
from .random_forest import random_forest
from .svc import svc

models:dict[str:object] = {
    'ada_boost': ada_boost,
    'gaussian_nb': gaussian_nb,
    'knc': knc,
    'logistic': logistic,
    'mlpc': mlpc,
    'random_forest': random_forest,
    'svc': svc
}