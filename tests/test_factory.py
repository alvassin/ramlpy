from ramlpy.typesystem import (
    Any, Nil, Boolean, String, Integer, Number, Array, Object, DateOnly,
    DateTime, DateTimeOnly, File, TimeOnly, Registry,
    Union)


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


def test_array_types(registry: Registry):
    assert type(registry.factory('[]')) is Array

    str_array = registry.factory('string[]')
    assert type(str_array) is Array
    assert type(str_array.items) is String

    str_array = registry.factory('number[][]')
    assert type(str_array) is Array
    assert type(str_array.items) is Array
    assert type(str_array.items.items) is Number


def test_union(registry: Registry):
    item = registry.factory('string | nil')
    assert type(item) is Union
    assert set([member.DEFINITION for member in item.members]) == {
        'string', 'nil'
    }


def test_custom(registry: Registry):
    registry.register('User', {
        'type': 'object',
        'properties': {
            'first': 'string',
            'last': 'string'
        }
    })

    user2 = registry.factory('User')
    assert type(user2) is Object


def test_multiple_inheritance(registry: Registry):
    registry.register('Int', {'type': 'integer', 'minimum': 2, 'maximum': 10})
    registry.register('Num', {'type': 'number', 'minimum': 5, 'maximum': 6})
    item = registry.factory('Int, Num')  # type: Integer
    assert type(item) is Integer
    assert item.minimum == 5
    assert item.maximum == 6


def test_multiple_inheritance_string(registry: Registry):
    registry.register('Any', {'type': 'any'})
    registry.register(
        'Str1', {'type': 'string', 'min_length': 2, 'max_length': 10}
    )
    registry.register(
        'Str2', {'type': 'string', 'min_length': 4, 'max_length': 6}
    )
    item = registry.factory('Any, Str1, Str2')  # type: String
    assert type(item) is String
    assert item.min_length == 4
    assert item.max_length == 6


def test_enum_derived(registry: Registry):
    registry.register('T1', {'enum': ['one', 'two']})
    registry.register('T2', {'enum': ['two', 'three']})
    t3 = registry.factory('T1, T2')
    assert t3.enum == {'two'}
