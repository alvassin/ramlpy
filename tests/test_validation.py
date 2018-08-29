import pytest

from ramlpy.exc import RAMLValidationError
from ramlpy.typesystem import (
    Any, Boolean, String,
    Number, Integer)


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
    item = String(required=True)
    item.validate('string')

    with pytest.raises(RAMLValidationError):
        item.validate(123)


def test_number_type():
    item = Number(required=True)
    item.validate(3.14)
    item.validate(0)
    item.validate(-6.5)

    with pytest.raises(RAMLValidationError):
        item.validate('non-boolean value')


def test_integer_type():
    item = Integer(required=True)
    item.validate(3)
    item.validate(0)
    item.validate(-1)

    with pytest.raises(RAMLValidationError):
        item.validate(3.14)
