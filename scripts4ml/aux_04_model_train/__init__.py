from .ada_boost import ada_boost
from .bernoulli_nb import bernoulli_nb
from .decision_tree import decision_tree
from .extra_trees import extra_trees
from .gaussian_nb import gaussian_nb
from .knc import knc
from .logistic import logistic
from .mlpc import mlpc
from .mlpc_256 import mlpc_256
from .mlpc_1024 import mlpc_1024
from .nearest_centroid import nearest_centroid
from .passive_aggressive import passive_aggressive
from .quadratic_discriminant import quadratic_discriminant
from .random_forest import random_forest
from .sgdc import sgdc
from .svc import svc
from .xgboost import xgboost
from .xgboost_1500 import xgboost_1500

models:dict[str:object] = {
    'ada_boost': ada_boost,
    'bernoulli_nb': bernoulli_nb,
    'decision_tree': decision_tree,
    'extra_trees': extra_trees, 
    'gaussian_nb': gaussian_nb,
    'knc': knc,
    'logistic': logistic,
    'mlpc': mlpc,
    'mlpc_1024': mlpc_1024,
    'mlpc_256': mlpc_256,
    'nearest_centroid': nearest_centroid,
    'passive_aggressive': passive_aggressive,
    'quadratic_discriminant': quadratic_discriminant,
    'random_forest': random_forest,
    'sgdc': sgdc,
    'svc': svc,
    'xgboost': xgboost,
    'xgboost_1500': xgboost_1500
}