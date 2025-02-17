import argparse
from typing import Callable

from decom.parsers import calculator_parser, measurand_parser, parameter_parser


def calculator(args) -> None:
    text = args.text
    pv = args.pv
    out = calculator_parser.parse(text)
    if isinstance(out, Callable):
        print(f"func(pv) = {out(pv)}")
    else:
        print(f"out = {out}")


def parameter(args) -> None:
    text = args.text
    print(f"Parameter Parser: {text!r}")
    out = parameter_parser.parse(text)
    print(f"out = {out}")


def measurand(args) -> None:
    text = args.text
    print(f"Mesurand Parser: {text!r}")
    out = measurand_parser.parse(text)
    print(f"out = {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="subcommand help")

    parser_c = subparsers.add_parser("calc", help="calculator")
    parser_c.add_argument("text")
    parser_c.add_argument("pv")
    parser_c.set_defaults(func=calculator)

    parser_p = subparsers.add_parser("param", help="parameter")
    parser_p.add_argument("text")
    parser_p.set_defaults(func=parameter)

    parser_m = subparsers.add_parser("meas", help="measurand")
    parser_m.add_argument("text")
    parser_m.set_defaults(func=measurand)

    args = parser.parse_args()
    args.func(args)
