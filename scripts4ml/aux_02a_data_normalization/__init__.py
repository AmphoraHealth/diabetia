from .box_cox import box_cox
from .quantile_transform import quantile_transform
from .yeo_johnson import yeo_johnson

normalizers:dict[str:object] = {
    'yeo_johnson': yeo_johnson,
    'box_cox': box_cox,
    'quantile_transform': quantile_transform
}