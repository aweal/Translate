#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup
import src.translate as translate

PACKAGE = "translate"
NAME = "translate"
DESCRIPTION = "pygtk application for translation text with yandex"
AUTHOR = "aweal"
AUTHOR_EMAIL = "gaweal@gmail.com"
URL = "github.com/aweal/translate"

VERSION = translate.__version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="BSD",
    url=URL,
    packages=['translate'],
    package_dir={'translate': 'src/translate'},

    data_files=[
        ("share/icons/hicolor/scalable/apps", ['resources/translate.svg']),
        ("share/icons/hicolor/48x48/apps", ['resources/translate.png']),
        ("share/applications", ['resources/Translate.desktop'])
    ],

    entry_points={'gui_scripts': [
        'translate = translate.application:run',
    ]},

    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    zip_safe=False, requires=['gi', 'requests'],
    test_suite="tests"
)
