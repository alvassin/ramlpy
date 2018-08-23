import pytest

from ramlpy.expressions import (
    MSG_UNPAIRED,
    MSG_UNEXPECTED_DELIMITER,
    MSG_UNEXPECTED_TYPE_DECLARATION,
    Token, Parser, RAMLTypeExprParseError,
)


def test_unexpected_expression():
    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('[]string')
    assert e.value.message == MSG_UNEXPECTED_TYPE_DECLARATION

    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('(string) any')
    assert e.value.message == MSG_UNEXPECTED_TYPE_DECLARATION

    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse(',,')
    assert e.value.message == MSG_UNEXPECTED_DELIMITER % Parser.INHERITANCE

    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('string,,any')
    assert e.value.message == MSG_UNEXPECTED_DELIMITER % Parser.INHERITANCE

    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('||')
    assert e.value.message == MSG_UNEXPECTED_DELIMITER % Parser.UNION

    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('string||any')
    assert e.value.message == MSG_UNEXPECTED_DELIMITER % Parser.UNION


def test_unpaired_array():
    values = {
        Parser.ARRAY_START: ['[', '[[', '[string', 'str[ing', 'string['],
        Parser.ARRAY_END: [']', ']]', ']string', 'str]ing', 'string]']
    }

    for char, strings in values.items():
        for string in strings:
            with pytest.raises(RAMLTypeExprParseError) as e:
                Parser.parse(string)
            assert e.value.message == MSG_UNPAIRED % char

    # FIXME: invalid message
    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('[string]')
    assert e.value.message == MSG_UNPAIRED % Parser.ARRAY_START


def test_unpaired_parenthesis():
    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('some string)')
    assert e.value.message == MSG_UNPAIRED % Parser.GROUP_END

    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('(some string')
    assert e.value.message == MSG_UNPAIRED % Parser.GROUP_START

    with pytest.raises(RAMLTypeExprParseError) as e:
        Parser.parse('some | (string')
    assert e.value.message == MSG_UNPAIRED % Parser.GROUP_START


def test_simple():
    item = Parser.parse('')
    assert item.kind == Token.SIMPLE
    assert item.value == ''

    item = Parser.parse('string')
    assert item.kind == Token.SIMPLE
    assert item.value == 'string'


def test_parse_groups():
    item = Parser.parse('(string)')
    assert item.kind == Token.SIMPLE
    assert item.value == 'string'

    item = Parser.parse('(((string)))')
    assert item.kind == Token.SIMPLE
    assert item.value == 'string'

    item = Parser.parse('(string)[]')
    assert item.kind == Token.ARRAY
    assert item.value.kind == Token.SIMPLE
    assert item.value.value == 'string'

    item = Parser.parse('(string | (integer | boolean))')
    assert item.kind == Token.UNION
    assert set([member.value for member in item.value]) == {
        'string', 'integer', 'boolean'
    }
    for member in item.value:
        assert member.kind == Token.SIMPLE


def test_array():
    item = Parser.parse('[]')
    assert item.kind == Token.ARRAY
    assert item.value is None

    item = Parser.parse('[][]')
    assert item.kind == Token.ARRAY
    assert item.value.kind == Token.ARRAY

    item = Parser.parse('string[]')
    assert item.kind == Token.ARRAY
    assert item.value.kind == Token.SIMPLE
    assert item.value.value == 'string'

    item = Parser.parse('string[][]')
    assert item.kind == Token.ARRAY
    assert item.value.kind == Token.ARRAY
    assert item.value.value.kind == Token.SIMPLE
    assert item.value.value.value == 'string'


def test_union():
    item = Parser.parse('any | any')
    assert item.kind == Token.UNION
    assert len(item.value) == 2
    for member in item.value:
        assert member.kind == Token.SIMPLE
        assert member.value == 'any'

    item = Parser.parse('any | number | integer')
    assert item.kind == Token.UNION
    assert set([member.value for member in item.value]) == {
        'any', 'number', 'integer'
    }
    for member in item.value:
        assert member.kind == Token.SIMPLE

    item = Parser.parse('[] | string[] | integer[]')
    assert item.kind == Token.UNION
    for member in item.value:
        assert member.kind == Token.ARRAY


def test_inherited():
    item = Parser.parse('any, string')
    assert item.kind == Token.INHERITED
    assert set([member.value for member in item.value]) == {'any', 'string'}
    for member in item.value:
        assert member.kind == Token.SIMPLE

    item = Parser.parse('any, number, integer')
    assert item.kind == Token.INHERITED
    assert set([member.value for member in item.value]) == {
        'any', 'number', 'integer'
    }
    for member in item.value:
        assert member.kind == Token.SIMPLE

    item = Parser.parse('any[], string[]')
    assert item.kind == Token.INHERITED
    for member in item.value:
        assert member.kind == Token.ARRAY


def test_complex():
    item = Parser.parse('any, string | integer')
    assert item.kind == Token.UNION
    assert set([member.kind for member in item.value]) == {
        Token.SIMPLE, Token.INHERITED
    }

    item = Parser.parse('any | number, integer')
    assert item.kind == Token.INHERITED
    assert set([member.kind for member in item.value]) == {
        Token.UNION, Token.SIMPLE
    }

    item = Parser.parse('integer[][][][] | string')
    assert item.kind == Token.UNION
    assert set([member.kind for member in item.value]) == {
        Token.SIMPLE, Token.ARRAY
    }
