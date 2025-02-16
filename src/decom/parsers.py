from lark import Lark

from decom.calculator import Calculator
from decom.symcalc import PVCalculator
from decom.transformers import MeasurandTransformer, ParameterTransformer

calculate_parser = Lark.open(
    "calculator.lark", rel_to=__file__, parser="lalr", transformer=Calculator()
)
symcalc_parser = Lark.open(
    "symcalc.lark", rel_to=__file__, parser="lalr", transformer=PVCalculator()
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
decom_parser = Lark.open("decom.lark", rel_to=__file__)
