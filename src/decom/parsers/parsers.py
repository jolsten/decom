import lark
from lark import Lark

from decom.calculator import CalculatorTransformer
from decom.measurand import MeasurandTransformer
from decom.parameter import ParameterTransformer

calculator_parser = Lark.open(
    "calculator.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=CalculatorTransformer(),
)
parameter_parser = Lark.open(
    "parameter.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=ParameterTransformer(),
)

MergedMeasurandTransformer = lark.visitors.merge_transformers(
    MeasurandTransformer(),
    parameter=ParameterTransformer(),
    calculator=CalculatorTransformer(),
)
measurand_parser = Lark.open(
    "measurand.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=MergedMeasurandTransformer,
)

decom_parser = Lark.open("decom.lark", rel_to=__file__, parser="lalr")
