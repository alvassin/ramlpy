import os

from ramlpy.parser import parse_raml_version, load


def test_parse_raml_version():
    assert parse_raml_version('#%RAML 1.0') == '1.0'


def test_parse_raml():
    load(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'example.raml'
    ))
