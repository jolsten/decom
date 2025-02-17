from lark import Lark

from decom.calculator import Calculator
from decom.transformers import MeasurandTransformer, ParameterTransformer

calculator_parser = Lark.open(
    "calculator.lark", rel_to=__file__, parser="lalr", transformer=Calculator()
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
