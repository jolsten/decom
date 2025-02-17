import logging
import sys
from typing import Callable

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
    if isinstance(func, Callable):
        print("func(pv) =", func(pv))
    else:
        print("func =", func)


if __name__ == "__main__":
    main()
