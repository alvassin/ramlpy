import pytest

from ramlpy.exc import RAMLTypeDefError
from ramlpy.typesystem import (
    Any, Array, Boolean, DateOnly, DateTime, DateTimeOnly, File, Integer,
    Nil, Number, Object, Registry, String, TimeOnly, Union
)


def test_simple_builtin_types(registry: Registry):
    assert type(registry.factory('')) is Any
    assert type(registry.factory('any')) is Any
    assert type(registry.factory('nil')) is Nil
    assert type(registry.factory('boolean')) is Boolean
    assert type(registry.factory('string')) is String
    assert type(registry.factory('number')) is Number
    assert type(registry.factory('integer')) is Integer
    assert type(registry.factory('date-only')) is DateOnly
    assert type(registry.factory('datetime')) is DateTime
    assert type(registry.factory('datetime-only')) is DateTimeOnly
    assert type(registry.factory('time-only')) is TimeOnly
    assert type(registry.factory('file')) is File
    assert type(registry.factory('array')) is Array
    assert type(registry.factory('object')) is Object


def test_array_type(registry: Registry):
    item = registry.factory('[]')
    assert type(item) is Array
    assert item.items is None

    item = registry.factory('string[]')
    assert type(item) is Array
    assert type(item.items) is String

    item = registry.factory('number[][]')
    assert type(item) is Array
    assert type(item.items) is Array
    assert type(item.items.items) is Number

    registry.register('Login', 'string')
    item = registry.factory('Login[]')
    assert type(item) is Array
    assert type(item.items) is String


def test_union_type(registry: Registry):
    item = registry.factory('string | nil')
    assert type(item) is Union
    assert {'string', 'nil'} == set([
        member.DEFINITION for member in item.members
    ])


def test_user_types(registry: Registry):
    registry.register('Login', {'type': 'string', 'min_length': 4})
    registry.register('User', {
        'type': 'object',
        'properties': {'name': 'string', 'login': 'Login'}
    })

    item = registry.factory('User')  # type: Object
    assert type(item) is Object
    assert type(item.properties['name']) is String
    assert type(item.properties['login']) is String


def test_multiple_inheritance(registry: Registry):
    registry.register('Int', {'type': 'integer', 'minimum': 2, 'maximum': 10})
    registry.register('Num', {'type': 'number', 'minimum': 5, 'maximum': 6})
    item = registry.factory('Int, Num')  # type: Integer
    assert type(item) is Integer
    assert item.minimum == 5
    assert item.maximum == 6


def test_multiple_inherited_string_facets(registry: Registry):
    registry.register('Any', {'type': 'any'})
    registry.register('Str1', {
        'type': 'string', 'min_length': 2, 'max_length': 10
    })
    registry.register('Str2', {
        'type': 'string', 'min_length': 4, 'max_length': 6
    })
    item = registry.factory('Any, Str1, Str2')  # type: String
    assert type(item) is String
    assert item.min_length == 4
    assert item.max_length == 6


def test_multiple_inherited_enum_facet(registry: Registry):
    registry.register('Type1', {'enum': ['one', 'two']})
    registry.register('Type2', {'enum': ['two', 'three']})
    registry.register('Type3', {'enum': ['zero', 'two']})
    registry.register('Type4', {'enum': ['zero', 'three']})

    item = registry.factory('Type1, Type2, Type3, string')
    assert item.enum == {'two'}

    with pytest.raises(RAMLTypeDefError):
        registry.factory('Type1, Type4')


def test_object_optional_properties(registry: Registry):
    item = registry.factory({
        'properties': {
            'login': 'string',
            'name?': 'string',
            'question??': 'string'
        }
    })

    assert item.properties['login'].required is True
    assert item.properties['name'].required is False
    assert item.properties['question?'].required is False


def test_nilable_types(registry: Registry):
    item = registry.factory('string?')
    assert type(item) is Union
    assert {'string', 'nil'} == set([
        member.DEFINITION for member in item.members
    ])

    item = registry.factory({'type': 'array', 'items': 'number?'})
    assert type(item) is Array
    assert type(item.items) is Union
    assert {'number', 'nil'} == set([
        member.DEFINITION for member in item.items.members
    ])

    item = registry.factory({
        'properties': {'name': 'integer?'}
    })
    assert type(item) is Object
    assert type(item.properties['name']) is Union
    assert {'integer', 'nil'} == set([
        member.DEFINITION for member in item.properties['name'].members
    ])
