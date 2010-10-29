#! /usr/bin/env python

try:
	from setuptools import setup
	
except ImportError:
	from distutils.core import setup
	
config = {
    "description": "Simple Comet",
	"version": 0.1,
	"license": "BSD",
	"author": "Frank Denis",
	"author_email": "j at pureftpd dot org",	
	"url": "http://github.com/jedisct1",
	"download_url": "http://github.com/jedisct1",
	"install_requires": [ "nose" ],
	"packages": [ "simple_comet" ],
	"scripts": [ "bin/simple-comet" ],
	"name": "simple_comet"
}

setup(**config)
