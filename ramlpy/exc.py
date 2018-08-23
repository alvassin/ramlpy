import typing


class RAMLError(RuntimeError):
    """ Base package error """
    pass


class RAMLTypeDefError(RAMLError):
    """ RAML data type definition error """
    pass


class RAMLTypeExprParseError(RAMLError):
    """ RAML type expression parsing error """
    def __init__(self, message: str):
        self.message = message


class RAMLValidationError(RAMLError):
    """ RAML data type validation error """
    __slots__ = ('message', 'field', 'errors')

    def __init__(
        self, message: str, *, field: str = None,
        errors: typing.Union[
            typing.List["RAMLValidationError"],
            typing.Mapping[str, "RAMLValidationError"]
        ] = None
    ):
        self.message = message
        self.field = field
        self.errors = errors
