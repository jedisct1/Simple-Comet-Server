#! /usr/bin/env python

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

CONFIG = {
    "description": "A simple Comet server",
    "version": 0.3,
    "license": "BSD",
    "author": "Frank Denis",
    "author_email": "j at pureftpd dot org",
    "url": "https://github.com/jedisct1/Simple-Comet-Server",
    "download_url": "https://github.com/jedisct1/Simple-Comet-Server",
    "install_requires": ["nose", "twisted", "simplejson"],
    "packages": ["simple_comet"],
    "scripts": ["bin/simple_comet"],
    "name": "simple_comet"
}

setup(**CONFIG)
