from .ada_boost import ada_boost
from .bernoulli_nb import bernoulli_nb
from .decision_tree import decision_tree
from .extra_trees import extra_trees
from .gaussian_nb import gaussian_nb
from .knc import knc
from .logistic import logistic
from .mlpc import mlpc
from .nearest_centroid import nearest_centroid
from .passive_aggressive import passive_aggressive
from .quadratic_discriminant import quadratic_discriminant
from .random_forest import random_forest
from .sgdc import sgdc
from .svc import svc
from .xgboost import xgboost

models:dict[str:object] = {
    'ada_boost': ada_boost,
    'bernoulli_nb': bernoulli_nb,
    'decision_tree': decision_tree,
    'extra_trees': extra_trees, 
    'gaussian_nb': gaussian_nb,
    'knc': knc,
    'logistic': logistic,
    'mlpc': mlpc,
    'nearest_centroid': nearest_centroid,
    'passive_aggressive': passive_aggressive,
    'quadratic_discriminant': quadratic_discriminant,
    'random_forest': random_forest,
    'sgdc': sgdc,
    'svc': svc,
    'xgboost': xgboost
}