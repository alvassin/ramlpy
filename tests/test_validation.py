import pytest

from ramlpy.exc import RAMLValidationError
from ramlpy.typesystem import (
    Any, Boolean, String,
    Number, Integer, Union, Array, Object)


def test_any_type():
    item = Any(required=True)
    with pytest.raises(RAMLValidationError):
        item.validate(None)

    item = Any(enum=['one', 'two'])
    with pytest.raises(RAMLValidationError):
        item.validate('three')


def test_boolean_type():
    item = Boolean(required=True)
    item.validate(True)
    item.validate(False)

    with pytest.raises(RAMLValidationError):
        item.validate('non-boolean value')


def test_string_type():
    item = String(required=True, min_length=2, max_length=6,
                  pattern='[a-zA-Z ]+')
    item.validate('string')

    with pytest.raises(RAMLValidationError):
        item.validate(123)

    with pytest.raises(RAMLValidationError):
        item.validate('a')

    with pytest.raises(RAMLValidationError):
        item.validate('too long')

    with pytest.raises(RAMLValidationError):
        item.validate('1nval1d')


def test_number_type():
    # FIXME: number format validation
    item = Number(required=True, minimum=-6.5, maximum=10.)
    item.validate(3.14)
    item.validate(0)
    item.validate(-6.5)

    with pytest.raises(RAMLValidationError):
        item.validate('non-number value')

    with pytest.raises(RAMLValidationError):
        item.validate(-6.6)

    with pytest.raises(RAMLValidationError):
        item.validate(10.1)


def test_integer_type():
    # FIXME: number format validation
    item = Integer(required=True, minimum=-777, maximum=777)
    item.validate(3)
    item.validate(0)
    item.validate(-1)

    with pytest.raises(RAMLValidationError):
        item.validate('non-integer value')

    with pytest.raises(RAMLValidationError):
        item.validate(3.14)

    with pytest.raises(RAMLValidationError):
        item.validate(-778)

    with pytest.raises(RAMLValidationError):
        item.validate(778)


def test_array_type():
    # FIXME: cover with tests unique_items
    item = Array()
    item.validate([])
    item.validate([1, 'two', False, {}])

    with pytest.raises(RAMLValidationError):
        item.validate(None)

    item = Array(items=String(), min_items=2, max_items=2)
    item.validate(['hello', 'world'])

    with pytest.raises(RAMLValidationError):
        item.validate([])

    with pytest.raises(RAMLValidationError):
        item.validate(['too', 'much', 'elements'])

    with pytest.raises(RAMLValidationError):
        item.validate([1, 2])


def test_object_type():
    item = Object(properties={
        'name': String(min_length=2),
        'gender': Any(enum=['male', 'female', 'by agreement of the parties'])
    })

    item.validate({
        'name': 'John',
        'gender': 'male'
    })

    with pytest.raises(RAMLValidationError):
        item.validate([])

    with pytest.raises(RAMLValidationError):
        item.validate(True)

    with pytest.raises(RAMLValidationError):
        item.validate('some string')


def test_union_type():
    item = Union(members={
        String(required=True),
        Integer(required=True)
    })

    item.validate('some string')
    item.validate(999)

    with pytest.raises(RAMLValidationError):
        item.validate(3.14)

    with pytest.raises(RAMLValidationError):
        item.validate(None)

    with pytest.raises(RAMLValidationError):
        item.validate(True)
