RAML parsing library for python
===============================

.. image:: https://coveralls.io/repos/github/alvassin/ramlpy/badge.svg?branch=master
    :target: https://coveralls.io/github/alvassin/ramlpy
    :alt: Coveralls

.. image:: https://travis-ci.org/alvassin/ramlpy.svg
    :target: https://travis-ci.org/alvassin/ramlpy
    :alt: Travis CI

.. image:: https://img.shields.io/pypi/v/ramlpy.svg
    :target: https://pypi.python.org/pypi/ramlpy/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/wheel/ramlpy.svg
    :target: https://pypi.python.org/pypi/ramlpy/

.. image:: https://img.shields.io/pypi/pyversions/ramlpy.svg
    :target: https://pypi.python.org/pypi/ramlpy/

.. image:: https://img.shields.io/pypi/l/ramlpy.svg
    :target: https://pypi.python.org/pypi/ramlpy/

*Library in very active development stage, is not recommended for use in production.*

**Supports only RAML 1.0 and Python 3.**

The main goal of this library:
 - Fast incoming HTTP requests validation (Resource URI, HTTP method, body)
 - Outgoing HTTP responses validation (when running test with CI)
 - Usable tool to use RAML Data types for validating any data structures (e.g. Rabbitmq queues, any other stuff your API is working with)
 
I also working on aiohttp middleware for super-easy integration, i plan to share it a little bit later.

Versioning
==========

This software follows `Semantic Versioning`_


.. _Semantic Versioning: http://semver.org/
