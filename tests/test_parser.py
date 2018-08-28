import os

from ramlpy.parser import parse_raml_version, load, Resource, Method


def test_parse_raml_version():
    assert parse_raml_version('#%RAML 1.0') == '1.0'


def test_parse_raml():
    doc = load(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'example.raml'
    ))

    resource = doc['/api/v1/ping']
    assert type(resource) is Resource
    assert type(resource.methods['get']) is Method
