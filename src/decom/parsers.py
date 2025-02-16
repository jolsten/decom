from lark import Lark

from decom.calculator import Calculator, PVCalculator
from decom.transformers import MeasurandTransformer, ParameterTransformer

calculate_parser = Lark.open(
    "calc_simple.lark", rel_to=__file__, parser="lalr", transformer=Calculator()
)
pv_calc_parser = Lark.open(
    "calc_pv.lark", rel_to=__file__, parser="lalr", transformer=PVCalculator()
)
parameter_parser = Lark.open(
    "parameter.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=ParameterTransformer(),
)
measurand_parser = Lark.open(
    "measurand.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=MeasurandTransformer(),
)
# decom_parser = Lark.open("decom.lark", rel_to=__file__)
