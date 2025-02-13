import sys
import lark

from decom.transformers import ParameterTransformer


parser = lark.Lark.open("src/decom/parameter.lark", transformer=ParameterTransformer(), parser="lalr")

def main():
    text = sys.argv[1]
    tree = parser.parse(text)
    try:
        print(tree.pretty())
    except AttributeError:
        print(tree)


if __name__ == "__main__":
    main()
