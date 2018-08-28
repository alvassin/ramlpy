import os

from setuptools import setup, find_packages
from importlib.machinery import SourceFileLoader


module_name = 'ramlpy'

module = SourceFileLoader(
    module_name,
    os.path.join(module_name, '__init__.py')
).load_module()


def load_requirements(fname):
    """ Load requirements from a pip requirements file """
    with open(fname) as f:
        line_iter = (line.strip() for line in f.readlines())
        return [line for line in line_iter if line and line[0] != '#']


setup(
    name=module_name.replace('_', '-'),
    version=module.__version__,
    author=module.__author__,
    author_email=module.authors_email,
    license=module.__license__,
    description=module.__doc__,
    long_description=open('README.rst').read(),
    platforms='all',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Microsoft',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=load_requirements('requirements.txt'),
    extras_require={
        'develop': load_requirements('requirements.dev.txt'),
    },
)
