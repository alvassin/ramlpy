from ramlpy.typesystem import (
    check_types_compatible as compatible,
    Any, Nil, Boolean, String, Number, Integer, DateOnly, DateTime,
    DateTimeOnly, TimeOnly, Array, Object, Union,
)


def test_any_compatible_types():
    assert compatible(Any.TYPE, Any.TYPE) is True
    assert compatible(Any.TYPE, Nil.TYPE) is True
    assert compatible(Any.TYPE, Boolean.TYPE) is True
    assert compatible(Any.TYPE, String.TYPE) is True
    assert compatible(Any.TYPE, Number.TYPE) is True
    assert compatible(Any.TYPE, Integer.TYPE) is True
    assert compatible(Any.TYPE, DateOnly.TYPE) is True
    assert compatible(Any.TYPE, DateTime.TYPE) is True
    assert compatible(Any.TYPE, DateTimeOnly.TYPE) is True
    assert compatible(Any.TYPE, TimeOnly.TYPE) is True
    assert compatible(Any.TYPE, Array.TYPE) is True
    assert compatible(Any.TYPE, Object.TYPE) is True
    assert compatible(Any.TYPE, Union.TYPE) is True


def test_nil_compatible_types():
    assert compatible(Nil.TYPE, Any.TYPE) is True
    assert compatible(Nil.TYPE, Nil.TYPE) is True
    assert compatible(Nil.TYPE, Boolean.TYPE) is False
    assert compatible(Nil.TYPE, String.TYPE) is False
    assert compatible(Nil.TYPE, Number.TYPE) is False
    assert compatible(Nil.TYPE, Integer.TYPE) is False
    assert compatible(Nil.TYPE, DateOnly.TYPE) is False
    assert compatible(Nil.TYPE, DateTime.TYPE) is False
    assert compatible(Nil.TYPE, DateTimeOnly.TYPE) is False
    assert compatible(Nil.TYPE, TimeOnly.TYPE) is False
    assert compatible(Nil.TYPE, Array.TYPE) is False
    assert compatible(Nil.TYPE, Object.TYPE) is False
    assert compatible(Nil.TYPE, Union.TYPE) is False
