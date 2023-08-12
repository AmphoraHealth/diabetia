
from .mixed import mixed
from .oversampling import oversampling
from .undersampling import undersampling
from .unbalanced import unbalanced

methods = {
  "unbalanced": unbalanced,
  "undersampling": undersampling,
  "oversampling": oversampling,
  "mixed": mixed
}