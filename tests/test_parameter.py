import pytest
from decom.parsers import parameter_parser
from decom.transformers import Parameter, Fragment


@pytest.mark.parametrize("text, expect", [
    ("[1]", Parameter([Fragment(1)])),
    ("[1+2]", Parameter([Fragment(1), Fragment(2)])),
    ("[1:1-4+2:5-8]", Parameter([Fragment(1, [1,2,3,4]), Fragment(2, [5,6,7,8])])),
])
def test_transformer(text: str, expect: Parameter):
    result = parameter_parser.parse(text)
    assert result == expect
