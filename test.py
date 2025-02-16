import logging
import sys

from lark import Lark, logger

from decom.calculator import PVCalculator

logger.setLevel(logging.DEBUG)
parser = Lark.open("src/decom/calc_pv.lark", transformer=PVCalculator(), parser="lalr")


def main():
    text = sys.argv[1]
    try:
        pv = int(sys.argv[2])
    except ValueError:
        pv = float(sys.argv[2])

    print("text =", text)
    func = parser.parse(text)
    print(func)
    print(func(pv))


if __name__ == "__main__":
    main()
