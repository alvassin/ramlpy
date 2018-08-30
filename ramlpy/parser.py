from collections import OrderedDict, defaultdict
from typing import Union, List, Any, Dict

import yaml
from ramlpy import typesystem
from ramlpy.exc import RAMLError
from ramlpy.typesystem import Registry
from ramlpy.utils import snake_case
from yarl import URL


HTTP_METHODS = [
    'get',
    'post',
    'delete',
    'put',
    'patch',
    'options',
    'head'
]


def parse_raml_version(header: str) -> str:
    """
    Parse RAML version from header.
    Line should look like "#%RAML 1.0".

    :param header: RAML header
    :type header: str

    :return: RAML format string
    :rtype: str

    :raise RAMLError: in case of parsing errors
    """
    chunks = header.split()
    if len(chunks) != 2:
        raise RAMLError("RAML header is invalid")

    if chunks[0] != "#%RAML":
        raise RAMLError("RAML header not found")

    return chunks[1]


def parse_method_body(
    body: Dict[str, Any],
    registry: Registry,
    default_media_types: Union[List[str], None]
):
    result = {}

    if isinstance(body, dict):
        explicit_media_types = False
        for item in body.keys():
            if '/' in item:
                explicit_media_types = True
                break

        if explicit_media_types:
            for media_type, request_body in body.items():
                result[media_type] = {}
                if 'type' in request_body:
                    result[media_type]['type'] = registry.factory(
                        request_body['type']
                    )
        else:
            # Default media types
            media_types = []
            if default_media_types is not None:
                media_types.extend(default_media_types)

            if not media_types:
                raise RuntimeError('No media types defined')

            for media_type in media_types:
                result[media_type] = {}
                if 'type' in body:
                    result[media_type]['type'] = registry.factory(body['type'])

    return result


def parse_method(
    data,
    registry: Registry,
    default_media_types: Union[List[str], None]
):
    result = {}

    if isinstance(data, dict):
        for item, value in data.items():
            if item == 'is':
                result['is_'] = value
            elif item == 'body':
                result['body'] = parse_method_body(
                    value,
                    registry,
                    default_media_types
                )
            elif item == 'responses':
                result['responses'] = {}
                if isinstance(value, dict):
                    for response_code, response in value.items():
                        result['responses'][response_code] = {}
                        if isinstance(response, dict):
                            for response_item, response_value in response.items():
                                if response_item == 'body':
                                    result['responses'][response_code][
                                        'body'
                                    ] = parse_method_body(
                                        response_value,
                                        registry,
                                        default_media_types
                                    )
                                else:
                                    result['responses'][response_code][
                                        response_item
                                    ] = response_value
            else:
                result[snake_case(item)] = value

    return Method(**result)


class Document:
    def __init__(
        self,
        title: str,
        description: str = None,
        version: str = None,
        base_uri: str = None,
        type_registry=None,
        resources=None
    ):
        self.title = title
        self.base_uri = base_uri
        self.description = description
        self.type_registry = type_registry
        self.resources = resources
        self.version = version

        self._resource_paths = OrderedDict()
        self.register_resource_paths(resources)

    def get_base_uri(self):
        if not self.base_uri:
            return ''

        base_uri = self.base_uri
        if '{version}' in base_uri and self.version:
            base_uri = base_uri.replace('{version}', self.version)

        return URL(base_uri).raw_path

    def register_resource_paths(self, resources, prefix: str = None):
        if prefix is None:
            prefix = self.get_base_uri()

        for resource_name, resource in resources.items():
            resource_path = ''.join([prefix, resource_name])
            if resource.methods or resource.resources:
                self._resource_paths[resource_path] = resource

                if resource.resources:
                    self.register_resource_paths(
                        resource.resources, prefix=resource_path
                    )

    def __getitem__(self, item):
        return self._resource_paths[item]

    def __contains__(self, item):
        return item in self._resource_paths


class Method:
    def __init__(
        self, *,
        display_name: str = None,
        responses=None,
        body=None,
        is_=None,
        secured_by=None
    ):
        self.display_name = display_name
        self.responses = responses
        self.body = body
        self.is_ = is_
        self.secured_by = secured_by


class Resource:
    def __init__(
        self, *,
        display_name: str = None,
        description: str = None,
        methods=None,
        resources=None,
        uri_parameters=None
    ):
        self.display_name = display_name
        self.description = description
        self.methods = methods
        self.resources = resources
        self.uri_parameters = uri_parameters


class Response:
    def __init__(
        self, *,
        description: str = None,
        headers=None,
        body=None
    ):
        self.description = description
        self.headers = headers
        self.body = body


def parse_resource(resource_name, data, registry, media_types):
    resource = {
        'methods': OrderedDict(),
        'resources': OrderedDict()
    }

    for property, value in data.items():
        if property.startswith('/'):
            resource['resources'][property] = parse_resource(
                property, value, registry
            )
        elif property.lower() in HTTP_METHODS:
            resource['methods'][property] = parse_method(value, registry, media_types)
        else:
            resource[snake_case(property)] = value

    return Resource(**resource)


def parse(data: str):
    # Read RAML header
    header, data = data.split('\n', 1)
    raml_version = parse_raml_version(header)
    if raml_version != '1.0':
        raise RAMLError('Unsupported RAML version')

    data = yaml.safe_load(data)

    media_types = data.get('mediaType')
    if isinstance(media_types, str):
        media_types = [media_types]

    registry = typesystem.Registry()
    if 'types' in data:
        registry.bulk_register(data['types'])

    resources = OrderedDict()
    for property_name, value in data.items():
        if property_name.startswith("/"):
            resources[property_name] = parse_resource(
                property_name, value, registry, media_types
            )

    document = Document(
        title=data.get('title'),
        base_uri=data.get('baseUri'),
        version=data.get('version'),
        type_registry=registry,
        resources=resources
    )

    return document


def load(uri: str):
    with open(uri) as stream:
        return parse(stream.read())
