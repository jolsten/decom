import logging
import sys

from lark import Lark, logger

from decom.calculator import CallableCalculator

logger.setLevel(logging.DEBUG)
parser = Lark.open(
    "src/decom/func_calc.lark", transformer=CallableCalculator(), parser="lalr"
)


def main():
    text = sys.argv[1]
    try:
        pv = int(sys.argv[2])
    except ValueError:
        pv = float(sys.argv[2])

    func = parser.parse(text)
    print(func(pv))


if __name__ == "__main__":
    main()
