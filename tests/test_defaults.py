from ramlpy.typesystem import (
    Any, Array, Boolean, Integer, Number, Object, String, Union
)


def test_any_type():
    item = Any(default=999)
    assert item.apply_defaults(None) == 999
    assert item.apply_defaults(1) == 1
    assert item.apply_defaults('custom') == 'custom'


def test_boolean_type():
    item = Boolean(default=True)
    assert item.apply_defaults(None) is True
    assert item.apply_defaults(False) is False


def test_string_type():
    item = String(default='default')
    assert item.apply_defaults(None) == 'default'
    assert item.apply_defaults('') == ''
    assert item.apply_defaults('custom') == 'custom'


def test_number_type():
    item = Number(default=3.14)
    assert item.apply_defaults(None) == 3.14
    assert item.apply_defaults(2.) == 2.
    assert item.apply_defaults(0.) == 0.


def test_integer_type():
    item = Integer(default=3)
    assert item.apply_defaults(None) == 3
    assert item.apply_defaults(2) == 2
    assert item.apply_defaults(0) == 0


def test_array_type():
    item = Array(default=[1, 2])
    assert item.apply_defaults(None) == [1, 2]
    assert item.apply_defaults([2, 3]) == [2, 3]
    assert item.apply_defaults([]) == []


def test_object_type():
    item = Object(properties={
        'name': String(default='Guest user'),
        'login': String(default='guest')
    })

    # Test defaults are set for missing properties
    assert item.apply_defaults({}) == {'name': 'Guest user', 'login': 'guest'}

    # Test defaults are set for properties with None value
    assert item.apply_defaults({'name': None, 'login': None}) == {
        'name': 'Guest user', 'login': 'guest'
    }

    # Test specified propeties override defaults
    specified = {'name': 'John Smith', 'login': 'john.smith'}
    assert item.apply_defaults(specified) == specified


def test_union_type():
    item = Union(members={String(), Integer()}, default='example')
    assert item.apply_defaults(None) == 'example'

    item = Union(members={String(), Integer()}, default=777)
    assert item.apply_defaults(None) == 777
