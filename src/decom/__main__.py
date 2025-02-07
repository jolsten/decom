import pathlib
from lark import Lark

path = pathlib.Path("src/decom/decom.lark")
grammar = path.read_text()
decom_parser = Lark(grammar)

if __name__ == "__main__":
    decom_text = pathlib.Path("tests/simple.decom").read_text()
    print(decom_parser.parse(decom_text).pretty())
