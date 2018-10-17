import os

from ramlpy.parser import parse_raml_version, load, Resource, Method, parse
from ramlpy import typesystem
from ramlpy.typesystem import Union


def test_parse_raml_version():
    assert parse_raml_version('#%RAML 1.0') == '1.0'


def test_parse_raml():
    doc = load(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data/examples/simple.raml'
    ))

    assert '/api/v1/feedback' in doc
    resource = doc['/api/v1/feedback']

    assert 'post' in resource.methods
    assert type(
        resource.methods['post'].body['application/json']['type']
    ) is typesystem.Object

    assert 'get' in resource.methods
    method = resource.methods['get']
    assert type(
        method.responses[200]['body']['application/json']['type']
    ) is typesystem.Array

    resource = doc['/api/v1/ping']
    assert type(resource) is Resource
    assert type(resource.methods['get']) is Method


# def test_example(registry: Registry):
#     registry.register('Human', {
#         'properties': {
#             'age': 'integer'
#         }
#     })
#
#     with pytest.raises(RAMLTypeDefError):
#         registry.factory({
#             'type': 'Human',
#             'properties': {'age': 'string'}
#         })


def test_nested_union_definition():
    RAML = """#%RAML 1.0
title: Example
version: 'v1'
baseUri: 'https://example.com/api/{version}'
types:
  Type1: string
  Type2: integer
  Type3: boolean
  Union1: Type1 | Type2
  Union2: Type1 | Type3
  Union3: Union1 | Union2
"""
    doc = parse(RAML)
    assert type(doc.type_registry.named_types['Union3']) is Union
    for member in doc.type_registry.named_types['Union3'].members:
        assert type(member) is Union
