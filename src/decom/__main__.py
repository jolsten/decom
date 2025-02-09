import pathlib
import argparse
from decom.parsers import decom_parser

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("decom", type=str, help="path to script")
    args = parser.parse_args()

    decom_text = pathlib.Path(args.decom).read_text()
    print(decom_parser.parse(decom_text).pretty())
