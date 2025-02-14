import pathlib

import pytest

from decom.parsers import decom_parser

decom_files = list(pathlib.Path("tests/scripts/").glob("*.decom"))


@pytest.mark.parametrize("decom_file", decom_files)
def test_lark(decom_file: pathlib.Path):
    text = decom_file.read_text()
    tree = decom_parser.parse(text)
    assert tree
