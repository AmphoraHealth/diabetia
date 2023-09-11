from .dummy import DummyFeatureSelection
from .xi2 import Xi2FeatureSelection
from .forward_selection import ProbabilisticForwardSelection
from .clinical_expertise import ClinicalExpertise
from .demographic import Demographic
from .demographic_diagnoses import DemographicDiagnoses
from .demographic_drugs import DemographicDrugs
from .demographic_labs import DemographicLabs

methods:dict[str:object] = {
    'dummy': DummyFeatureSelection,
    'xi2': Xi2FeatureSelection,
    'probabilistic':ProbabilisticForwardSelection,
    'clinical_expertise':ClinicalExpertise,
    'demographic': Demographic,
    'demographic_diagnoses': DemographicDiagnoses,
    'demographic_drugs': DemographicDrugs,
    'demographic_labs': DemographicLabs
}
