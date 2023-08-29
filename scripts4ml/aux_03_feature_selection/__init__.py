from .dummy import DummyFeatureSelection
from .xi2 import Xi2FeatureSelection
from .forward_selection import ProbabilisticForwardSelection

methods:dict[str:object] = {
    'dummy': DummyFeatureSelection,
    'xi2': Xi2FeatureSelection,
    'probabilistic':ProbabilisticForwardSelection
}
