import pathlib
from lark import Lark

grammar = (pathlib.Path(__file__).parent / "decom.lark").read_text()
decom_parser = Lark(grammar)
