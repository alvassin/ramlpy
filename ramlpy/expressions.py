from ramlpy.exc import RAMLTypeExprParseError


MSG_UNPAIRED = 'No pair for "%s" char'
MSG_UNEXPECTED_TYPE_DECLARATION = (
    'Unexpected type declaration: modifier/delimiter expected'
)
MSG_UNEXPECTED_DELIMITER = (
    'Unexpected delimiter "%s": expression expected'
)


class Token:
    # Simple tokens do not have arguments, array can be shown as simple token,
    # when used without brackets
    SIMPLE = 'simple'
    ARRAY = 'array'
    UNION = 'union'
    INHERITED = 'inherited'
    __slots__ = 'kind', 'value'

    def __init__(self, kind: str, value=None):
        self.kind = kind
        self.value = value

    def __repr__(self):
        return (
            '<{module}.{name}(kind={kind}, value={value}) object at 0x{id:x}>'
        ).format(
            module=self.__module__, name=self.__class__.__name__,
            kind=self.kind, value=self.value, id=id(self)
        )


class Parser:
    ARRAY_START = '['
    ARRAY_END = ']'
    GROUP_START = '('
    GROUP_END = ')'
    INHERITANCE = ','
    UNION = '|'

    _special_chars = [
        ARRAY_START, ARRAY_END,
        GROUP_START, GROUP_END,
        INHERITANCE, UNION
    ]

    @classmethod
    def is_simple(cls, expression: str) -> bool:
        for char in cls._special_chars:
            if char in expression:
                return False
        return True

    @classmethod
    def parse(cls, expression: str) -> Token:
        expression = expression.strip()

        if cls.is_simple(expression):
            return Token(Token.SIMPLE, expression)

        buffer = ''
        current_item = None
        items = []
        group = 0
        delimiter = None

        for pos, char in enumerate(expression):
            if char == cls.GROUP_START:
                group += 1

            elif char == cls.GROUP_END:
                group -= 1

                if group < 0:
                    raise RAMLTypeExprParseError(MSG_UNPAIRED % cls.GROUP_END)

                if group == 0:
                    if current_item is not None:
                        raise RAMLTypeExprParseError(
                            MSG_UNEXPECTED_TYPE_DECLARATION
                        )

                    current_item = cls.parse(buffer.strip())
                    buffer = ''

            elif char == cls.ARRAY_START and not group:
                if (
                    pos == len(expression) - 1 or
                    expression[pos + 1] != cls.ARRAY_END
                ):
                    raise RAMLTypeExprParseError(MSG_UNPAIRED % cls.ARRAY_START)

            elif char == cls.ARRAY_END and not group:
                if pos == 0 or expression[pos - 1] != cls.ARRAY_START:
                    raise RAMLTypeExprParseError(MSG_UNPAIRED % cls.ARRAY_END)

                buffer = buffer.strip()
                if buffer:
                    current_item = cls.parse(buffer)
                    buffer = ''

                current_item = Token(Token.ARRAY, current_item)

            elif char in [cls.UNION, cls.INHERITANCE] and not group:
                buffer = buffer.strip()
                if buffer:
                    if current_item is not None:
                        raise RAMLTypeExprParseError(
                            MSG_UNEXPECTED_TYPE_DECLARATION
                        )

                    current_item = cls.parse(buffer)
                    buffer = ''

                if current_item is None:
                    raise RAMLTypeExprParseError(
                        MSG_UNEXPECTED_DELIMITER % char
                    )

                items.append(current_item)
                current_item = None

                if char != delimiter and len(items) > 1:
                    items = [Token(
                        (
                            Token.UNION if delimiter == cls.UNION
                            else Token.INHERITED
                        ),
                        value=items
                    )]

                delimiter = char
            else:
                buffer += char

        # Final processing
        if group > 0:
            raise RAMLTypeExprParseError(MSG_UNPAIRED % cls.GROUP_START)

        buffer = buffer.strip()
        if buffer:
            if current_item is not None:
                raise RAMLTypeExprParseError(MSG_UNEXPECTED_TYPE_DECLARATION)
            current_item = cls.parse(buffer)

        if current_item:
            items.append(current_item)

        if len(items) > 1:
            items = [Token(
                Token.UNION if delimiter == cls.UNION else Token.INHERITED,
                value=items
            )]

        return items[0]


__all__ = ('Token', 'Parser', 'RAMLTypeExprParseError')
