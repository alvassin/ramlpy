import pytest

from ramlpy.typesystem import Registry


@pytest.fixture()
def registry() -> Registry:
    return Registry()
