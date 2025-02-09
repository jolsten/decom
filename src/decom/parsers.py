from lark import Lark
from decom.transformers import CalculateTree

calculate_parser = Lark.open("calculator.lark", rel_to=__file__, parser='lalr', transformer=CalculateTree())
parameter_parser = Lark.open("parameter.lark", rel_to=__file__)
measurand_parser = Lark.open("measurand.lark", rel_to=__file__)
decom_parser = Lark.open("decom.lark", rel_to=__file__)
