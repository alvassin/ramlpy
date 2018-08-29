import re
import typing
from enum import Enum
from itertools import chain

from .exc import RAMLValidationError, RAMLTypeDefError
from .expressions import Parser, Token
from .utils import snake_case, topological_sort


class Any:
    DEFINITION = 'any'
    TYPE = 'any'

    __slots__ = (
        'display_name', 'description',
        'required', 'default', 'enum', 'example', 'examples',
    )

    def __init__(
        self, *,
        display_name: str = None,
        description: str = None,
        required: bool = True,
        enum: typing.Iterable = None,
        default=None,
        example=None,
        examples: typing.Mapping[str, typing.Any] = None,
    ):
        self.display_name = display_name
        self.description = description
        self.required = required
        self.enum = enum
        self.default = default
        self.example = example
        self.examples = examples

    def apply_defaults(self, value):
        if value is None and self.default is not None:
            value = self.default
        return value

    def validate(self, value):
        if self.required and value is None:
            raise RAMLValidationError('Missing value for the required field')

        if self.enum and value not in self.enum:
            raise RAMLValidationError(
                'Value %s does not match allowed values' % value
            )

    def get_definition(self) -> typing.Dict[str, typing.Any]:
        slots = chain.from_iterable(
            getattr(cls, '__slots__', [])
            for cls in self.__class__.__mro__
        )

        return {
            slot: getattr(self, slot)
            for slot in slots
        }

    @classmethod
    def get_params_for_derived_class(cls, parent_types):
        enum = None
        for parent_type in parent_types:
            parent_enum = getattr(parent_type, 'enum', None)
            if parent_enum:
                if enum is None:
                    enum = parent_enum
                else:
                    # find intersection
                    enum = set(enum).intersection(set(parent_enum))
                    if not enum:
                        raise RAMLTypeDefError('enum conflict')

        return {
            'enum': enum
        }


class Nil(Any):
    DEFINITION = 'nil'
    TYPE = 'any:nil'

    def validate(self, value: None):
        if value is not None:
            raise RAMLValidationError(
                'Value is expected to be nil / null / None'
            )


class Boolean(Any):
    DEFINITION = 'boolean'
    TYPE = 'any:boolean'

    def validate(self, value):
        super().validate(value)

        if value is not None and type(value) is not bool:
            raise RAMLValidationError('Value is expected to be boolean')


class String(Any):
    DEFINITION = 'string'
    TYPE = 'any:string'
    MIN_LENGTH = 0
    MAX_LENGTH = 2147483647

    __slots__ = 'pattern', 'min_length', 'max_length',

    def __init__(
        self, *, pattern: str = None, min_length: int = MIN_LENGTH,
        max_length: int = MAX_LENGTH, **kwargs
    ):
        super().__init__(**kwargs)
        self.pattern = pattern
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) is not str:
            raise RAMLValidationError('Value is expected to be string')

        value_length = len(value)
        if self.max_length and value_length > self.max_length:
            raise RAMLValidationError(
                'Value is too long: given %d, max allowed %d' % (
                    value_length, self.max_length
                )
            )

        if self.min_length and value_length < self.min_length:
            raise RAMLValidationError(
                'Value is too short: given %d, min allowed %d' % (
                    value_length, self.max_length
                )
            )

        if self.pattern:
            if re.match(self.pattern, value) is None:
                raise RAMLValidationError(
                    'Value %s does not match pattern %s' % (
                        value, self.pattern
                    )
                )

    @classmethod
    def get_params_for_derived_class(cls, parent_types):
        params = super().get_params_for_derived_class(parent_types)
        params.update({
            'min_length': cls.MIN_LENGTH,
            'max_length': cls.MAX_LENGTH,
            'pattern': None
        })

        for parent_type in parent_types:
            parent_min_length = getattr(parent_type, 'min_length',
                                        cls.MIN_LENGTH)

            if parent_min_length > params['min_length']:
                params['min_length'] = parent_min_length

            parent_max_length = getattr(parent_type, 'max_length',
                                        cls.MAX_LENGTH)

            if parent_max_length < params['max_length']:
                params['max_length'] = parent_max_length

            if (
                hasattr(parent_type, 'pattern') and
                getattr(parent_type, 'pattern') is not None
            ):
                if params['pattern'] is not None:
                    raise RuntimeError('Pattern definition conflict')
                params['pattern'] = getattr(parent_type, 'pattern')

        return params


class NumberFormat(Enum):
    """
    int8: (-128 to 127)
    int16: (-32,768 to +32,767)
    int32, int: (-2,147,483,648 to +2,147,483,647)
    int64, long: (-9,223,372,036,854,775,808 to +9,223,372,036,854,775,807)
    """
    int = 'int'
    int8 = 'int8'
    int16 = 'int16'
    int32 = 'int32'
    int64 = 'int64'
    long = 'long'
    float = 'float'
    double = 'double'


class Number(Any):
    DEFINITION = 'number'
    TYPE = 'any:number'

    __slots__ = 'minimum', 'maximum', 'format', 'multiple_of',

    def __init__(
        self, *,
        minimum: typing.Union[int, float] = None,
        maximum: typing.Union[int, float] = None,
        format: NumberFormat = None,
        multiple_of: typing.Union[int, float] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.minimum = minimum
        self.maximum = maximum
        self.format = format
        self.multiple_of = multiple_of

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) not in (float, int):
            raise RAMLValidationError('Value is expected to be number')

        if self.minimum is not None and self.minimum > value:
            raise RAMLValidationError(
                'Value %r is less than allowed minimum %r' % (
                    value, self.minimum
                )
            )

        if self.maximum is not None and self.maximum < value:
            raise RAMLValidationError(
                'Value %r is geater than allowed maximum %r' % (
                    value, self.maximum
                )
            )

        if self.multiple_of is not None and value % self.multiple_of != 0:
            raise RAMLValidationError(
                'Value %r is not divisible with %r' % (value, self.multiple_of)
            )

        if self.format is not None:
            # FIXME: currently not clear in documentation how to validate
            raise NotImplementedError()

    @classmethod
    def get_params_for_derived_class(cls, parent_types):
        params = {
            'minimum': None,
            'maximum': None,
            'format': None,
            'multiple_of': None,
        }

        for parent_type in parent_types:
            if hasattr(parent_type, 'minimum'):
                if (
                    params['minimum'] is None or
                    params['minimum'] < getattr(parent_type, 'minimum')
                ):
                    params['minimum'] = getattr(parent_type, 'minimum')

            if hasattr(parent_type, 'maximum'):
                if (
                    params['maximum'] is None or
                    params['maximum'] > getattr(parent_type, 'maximum')
                ):
                    params['maximum'] = getattr(parent_type, 'maximum')

            if getattr(parent_type, 'format') is not None:
                if params['format'] is not None:
                    raise RuntimeError('format definition conflict')
                params['format'] = getattr(parent_type, 'format')

            if getattr(parent_type, 'multiple_of') is not None:
                if params['multiple_of'] is not None:
                    raise RuntimeError('multiple_of definition conflict')
                params['multiple_of'] = getattr(parent_type, 'multiple_of')

        return params


class Integer(Number):
    DEFINITION = 'integer'
    TYPE = 'any:number:integer'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def validate(self, value):
        super().validate(value)
        if value is not None and type(value) is not int:
            raise RAMLValidationError('Value is expected to be integer')


class DateOnly(Any):
    DEFINITION = 'date-only'
    TYPE = 'any:date-only'

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()


class TimeOnly(Any):
    DEFINITION = 'time-only'
    TYPE = 'any:time-only'

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()


class DateTimeOnly(Any):
    DEFINITION = 'datetime-only'
    TYPE = 'any:datetime-only'

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()


class DateFormat(Enum):
    rfc3339 = 'rfc3339'
    rfc2616 = 'rfc2616'


class DateTime(Any):
    DEFINITION = 'datetime'
    TYPE = 'any:datetime'

    __slots__ = 'format',

    def __init__(self, *, format: DateFormat = DateFormat.rfc3339, **kwargs):
        super().__init__(**kwargs)
        self.format = format

    def validate(self, value: str):
        super().validate(value)
        raise NotImplementedError()


class File(Any):
    DEFINITION = 'file'
    TYPE = 'any:file'
    MIN_LENGTH = 0
    MAX_LENGTH = 2147483647

    __slots__ = 'file_types', 'min_length', 'max_length',

    def __init__(
        self, *,
        file_types: typing.List[str] = None,
        min_length: int = MIN_LENGTH,
        max_length: int = MAX_LENGTH,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.file_types = file_types
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value):
        super().validate(value)
        raise NotImplementedError()


class Array(Any):
    DEFINITION = 'array'
    TYPE = 'any:array'

    __slots__ = 'unique_items', 'items', 'min_items', 'max_items',

    def __init__(
        self, *,
        unique_items: bool = False,
        items: Any = None,
        min_items: int = 0,
        max_items: int = 2147483647,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.unique_items = unique_items
        self.items = items
        self.min_items = min_items
        self.max_items = max_items

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) is not list:
            raise RAMLValidationError('Value is expected to be list')

        if self.items is not None:
            for value_item in value:
                self.items.validate(value_item)

        value_length = len(value)
        if (self.max_items is not None) and (value_length > self.max_items):
            raise RAMLValidationError('Too many items: given %d, allowed %d' % (
                value_length, self.max_items
            ))

        if (self.min_items is not None) and (value_length < self.min_items):
            raise RAMLValidationError(
                'Not enough items: given %d, minimum required %d' % (
                    value_length, self.min_items
                )
            )

        if self.unique_items:
            # FIXME: todo
            raise NotImplementedError()


class Object(Any):
    DEFINITION = 'object'
    TYPE = 'any:object'

    __slots__ = (
        'properties', 'min_properties', 'max_properties',
        'additional_properties', 'discriminator', 'discriminator_value'
    )

    def __init__(
        self, *,
        properties: typing.Mapping[str, Any] = None,
        min_properties: int = None,
        max_properties: int = None,
        additional_properties: bool = True,
        discriminator: str = None,
        discriminator_value: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.properties = properties or dict()
        self.min_properties = min_properties
        self.max_properties = max_properties
        self.additional_properties = additional_properties
        self.discriminator = discriminator
        self.discriminator_value = discriminator_value

    def validate(self, value):
        super().validate(value)

        if value is None:
            return

        if type(value) is not dict:
            raise RAMLValidationError('Value is expected to be object')

        errors = {}
        for property_name, property in self.properties.items():
            try:
                property.validate(value.get(property_name))
            except RAMLValidationError as error:
                errors[property_name] = error

        if errors:
            raise RAMLValidationError('Object contains errors', errors=errors)

        defined_properties_number = len(self.properties)
        if (
            self.min_properties is not None and
            self.min_properties > defined_properties_number
        ):
            raise RAMLValidationError(
                'Object should have at least %d properties, %d provided' % (
                    self.min_properties, defined_properties_number
                )
            )

        if (
            self.max_properties is not None and
            self.max_properties < defined_properties_number
        ):
            raise RAMLValidationError(
                'Object should have maximum %d properties, %d provided' % (
                    self.max_properties, defined_properties_number
                )
            )

    def apply_defaults(self, value: typing.Dict[str, typing.Any]):
        for name, property in self.properties.items():
            if value.get(name) is None and property.default is not None:
                value[name] = property.default
        return value


class Union(Any):
    DEFINITION = None
    TYPE = 'any:union'

    __slots__ = 'members',

    def __init__(self, *, members: typing.Set[Any], **kwargs):
        super().__init__(**kwargs)
        self.members = members

    def validate(self, value):
        super().validate(value)

        errors = []
        for member in self.members:
            try:
                member.validate(value)
                break
            except RAMLValidationError as error:
                errors.append(error)

        else:
            raise RAMLValidationError('All union members failed', errors=errors)


def check_types_compatible(*types: str) -> bool:
    """
    Check types have no conflicts (can be used in multiple inheritance)
    """
    cur_type = None
    cur_type_segments = None

    for data_type in types:
        segments = data_type.count(':')
        if (cur_type is None) or (segments >= cur_type_segments):
            cur_type_segments = segments
            cur_type = data_type

    for data_type in types:
        if data_type not in cur_type:
            return False

    return True


def get_precisest_type(*types: str) -> str:
    """
    Choose precisest type or raise RAMLTypeDefError
    if provided types are not compatible.
    """
    cur_type = None
    max_segments = 0

    for data_type in types:
        segments = data_type.count(':')
        if segments > max_segments or cur_type is None:
            max_segments = segments
            cur_type = data_type

    for data_type in types:
        if data_type not in cur_type:
            raise RAMLTypeDefError(
                'Incompatible types: %r %r' % (cur_type, data_type)
            )

    return cur_type


BUILTIN_TYPES = [
    Any, Array, Boolean, DateOnly, DateTime, DateTimeOnly,
    File, Integer, Nil, Number, Object, String, TimeOnly
]

TypeDefStruct = typing.Dict[str, typing.Any]
TypeDefExpr = str


class Registry:
    BUILTIN_TYPE_CLASS_MAP = {
        builtin_type.DEFINITION: builtin_type
        for builtin_type in BUILTIN_TYPES
    }

    def __init__(self, types: typing.Dict[str, typing.Any] = None):
        self.named_types = {}
        self.expr_parser = Parser()

    def register(
        self, name: str, definition: typing.Union[TypeDefExpr, TypeDefStruct]
    ) -> Any:
        self.named_types[name] = self.factory(definition=definition)
        return self.named_types[name]

    def bulk_register(self, named_definitions: typing.Dict[str, typing.Any]):
        """ Add multiple named declarations to registry instance. """
        dependencies = [
            [name, self.parse_dependencies(definition)]
            for name, definition in named_definitions.items()
        ]
        sorted_definitions = topological_sort(dependencies)

        for name in sorted_definitions:
            self.register(name=name, definition=named_definitions[name])

    @classmethod
    def parse_dependencies(
        cls,
        definition: typing.Union[TypeDefExpr, TypeDefStruct]
    ) -> typing.Set[str]:
        """ Get named types dependency set for given definition. """
        definition = cls.normalize_definition(definition)

        # Arrays can have depencencies in items attribute
        if definition['type'] == Array.DEFINITION and 'items' in definition:
            return cls.parse_dependencies(definition.get('items'))

        # Objects can contain dependencies in properties attribute
        elif (
            definition['type'] == Object.DEFINITION and
            'properties' in definition
        ):
            dependencies = []
            for _, property in definition.get('properties').items():
                dependencies.extend(cls.parse_dependencies(property))
            return set(dependencies)

        # Simple cases, just definition type
        else:
            def_type = definition['type']
            for special_char in ['(', ')', '[', ']', ',', '|']:
                def_type = def_type.replace(special_char, ' ')

        dependencies = set(def_type.split()) - set(
            cls.BUILTIN_TYPE_CLASS_MAP.keys()
        )
        if dependencies:
            pass
        return dependencies

    def _resolve_token(
        self, token: Token
    ) -> typing.Tuple[type, typing.Dict[str, typing.Any]]:
        if token.kind == Token.SIMPLE:
            if token.value == '':
                return Any, {}
            if token.value[-1] == '?':
                return self._resolve_token(
                    Token(
                        kind=Token.UNION,
                        value=[
                            Token(kind=token.kind, value=token.value[:-1]),
                            Token(kind=Token.SIMPLE, value='nil')
                        ]
                    )
                )
            elif token.value in self.BUILTIN_TYPE_CLASS_MAP:
                return self.BUILTIN_TYPE_CLASS_MAP[token.value], {}
            else:
                user_type = self.named_types[token.value]
                return user_type.__class__, user_type.get_definition()

        elif token.kind == Token.ARRAY:
            type_kwargs = {}
            if token.value:
                items_class, items_kwargs = self._resolve_token(token.value)
                type_kwargs = {'items': items_class(**items_kwargs)}
            return Array, type_kwargs

        elif token.kind == Token.INHERITED:
            members = []
            for member in token.value:
                member_cls, member_kwargs = self._resolve_token(member)
                members.append(member_cls(**member_kwargs))

            precisest_type = get_precisest_type(*[
                member.TYPE for member in members
            ])

            type_cls = self.BUILTIN_TYPE_CLASS_MAP[
                precisest_type.split(':')[-1]
            ]
            # Нужно учитывать что мы выбираем наиболее строгие параметры
            type_kwargs = type_cls.get_params_for_derived_class(members)

            return type_cls, type_kwargs

        elif token.kind == Token.UNION:
            members = []
            for member in token.value:
                member_class, member_kwargs = self._resolve_token(member)
                members.append(member_class(**member_kwargs))

            return Union, {'members': members}

    def factory(
        self,
        definition: typing.Union[TypeDefExpr, TypeDefStruct],
        extra_kwargs=None
    ) -> Any:
        """
        Instantiate data type from definition.
        Definition may be RAML type expression or dict.
        """
        definition = self.normalize_definition(definition)
        if extra_kwargs:
            definition.update(extra_kwargs)

        kwargs = {
            snake_case(key): value
            for key, value in definition.items()
            if key not in ['type', 'properties']
        }

        token = self.expr_parser.parse(definition['type'])
        type_class, type_kwargs = self._resolve_token(token)

        if type_class is Array and 'items' in definition:
            if 'items' in type_kwargs:
                raise RuntimeError('Items can not be defined twice!')

            kwargs['items'] = self.factory(definition['items'])

        if type_class is Object and 'properties' in definition:
            kwargs['properties'] = {}
            for prop_name, prop_val in definition['properties'].items():
                extra_kwargs = {}
                if prop_name[-1] == '?':
                    extra_kwargs['required'] = False
                    prop_name = prop_name[:-1]

                kwargs['properties'][prop_name] = self.factory(
                    definition=prop_val,
                    extra_kwargs=extra_kwargs
                )

        return type_class(**{**type_kwargs, **kwargs})

    @classmethod
    def normalize_definition(
        cls,
        definition: typing.Union[TypeDefExpr, TypeDefStruct]
    ) -> TypeDefStruct:
        """
        Get normalized type definition.
        Normalized definition is a dict with 'type' key.
        """
        if type(definition) is str:
            definition = {'type': definition}

        elif type(definition) is not dict:
            raise RAMLTypeDefError(
                'Invalid definition type, str or dict expected'
            )

        if definition.get('type') is None:
            if 'properties' in definition:
                definition['type'] = Object.DEFINITION
            else:
                definition['type'] = Any.DEFINITION

        return definition
