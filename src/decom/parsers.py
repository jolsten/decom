from lark import Lark

from decom.transformers import CalculateTree, MeasurandTransformer, ParameterTransformer

calculate_parser = Lark.open(
    "calculator.lark", rel_to=__file__, parser="lalr", transformer=CalculateTree()
)
parameter_parser = Lark.open(
    "parameter.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=ParameterTransformer(),
    # debug=True,
)
measurand_parser = Lark.open(
    "measurand.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=MeasurandTransformer(),
    # strict=True,
)
decom_parser = Lark.open("decom.lark", rel_to=__file__)
