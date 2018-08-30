import os

from ramlpy.parser import parse_raml_version, load, Resource, Method
from ramlpy import typesystem


def test_parse_raml_version():
    assert parse_raml_version('#%RAML 1.0') == '1.0'


def test_parse_raml():
    doc = load(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'example.raml'
    ))

    assert '/api/v1/feedback' in doc
    resource = doc['/api/v1/feedback']

    assert 'post' in resource.methods
    assert type(
        resource.methods['post'].body['application/json']['type']
    ) is typesystem.Object

    assert 'get' in resource.methods
    assert type(
        resource.methods['get'].responses[200]['body']['application/json']['type']
    ) is typesystem.Array



    resource = doc['/api/v1/ping']
    assert type(resource) is Resource
    assert type(resource.methods['get']) is Method
