""" RAML parsing library """
try:
    from .version import __version__, version_info
except ImportError:
    version_info = (0, 0, 0)
    __version__ = '{}.{}.{}'.format(*version_info)


authors = (
    ('Alexander Vasin', 'hi@alvass.in'),
)

authors_email = ", ".join(
    '{}'.format(email) for _, email in authors
)

__license__ = 'MIT',
__author__ = ", ".join(
    '{} <{}>'.format(name, email) for name, email in authors
)

# It's same persons right now
__maintainer__ = __author__

__all__ = (
    '__author__', '__author__', '__license__',
    '__maintainer__', '__version__',
    'version_info',
)
