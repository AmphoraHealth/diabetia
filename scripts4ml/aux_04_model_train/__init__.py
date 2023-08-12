from .ada_boost import ada_boost
from .gaussian import gaussian
from .knc import knc
from .logistic import logistic
from .mlpc import mlpc
from .random_forest import random_forest
from .svc import svc

models:dict[str:object] = {
    'ada_boost': ada_boost,
    'gaussian': gaussian,
    'knc': knc,
    'logistic': logistic,
    'mlpc': mlpc,
    'random_forest': random_forest,
    'svc': svc
}