from ramlpy.typesystem import (
    Any, Array, Boolean, Integer, Number, Object, String, Union
)


def test_any_type():
    item = Any(default=999)
    assert item.validate(None) == 999
    assert item.validate(1) == 1


def test_boolean_type():
    item = Boolean(default=True)
    assert item.validate(None) is True
    assert item.validate(False) is False


def test_string_type():
    item = String(default='default')
    assert item.validate(None) == 'default'
    assert item.validate('') == ''


def test_number_type():
    item = Number(default=3.14)
    assert item.validate(None) == 3.14
    assert item.validate(2.) == 2.
    assert item.validate(0.) == 0.


def test_integer_type():
    item = Integer(default=3)
    assert item.validate(None) == 3
    assert item.validate(2) == 2
    assert item.validate(0) == 0


def test_array_type():
    item = Array(default=[1, 2])
    assert item.validate(None) == [1, 2]
    assert item.validate([2, 3]) == [2, 3]
    assert item.validate([]) == []

    item = Array(items=String(default='test'))
    assert item.validate([None]) == ['test']


def test_object_type():
    item = Object(properties={
        'name': String(default='Guest user'),
        'login': String(default='guest')
    })

    # Test defaults are set for missing properties
    assert item.validate({}) == {'name': 'Guest user', 'login': 'guest'}

    # Test defaults are set for properties with None value
    assert item.validate({'name': None, 'login': None}) == {
        'name': 'Guest user', 'login': 'guest'
    }

    # Test specified propeties override defaults
    specified = {'name': 'John Smith', 'login': 'john.smith'}
    assert item.validate(specified) == specified


def test_union_type():
    item = Union(members={String(), Integer()}, default='example')
    assert item.validate(None) == 'example'

    item = Union(members={String(), Integer()}, default=777)
    assert item.validate(None) == 777
