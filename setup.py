"""See README.md for package documentation."""

from setuptools import setup, find_namespace_packages

from io import open
from os import path

here = path.abspath(path.dirname(__file__))

filename = path.join(here, 'kivy_garden', 'hover', '_version.py')
locals = {}
with open(filename, 'rb') as fh:
    exec(compile(fh.read(), filename, 'exec'), globals(), locals)
__version__ = locals['__version__']

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

URL = 'https://github.com/pythonic64/hover'

setup(
    name='kivy_garden.hover',
    version=__version__,
    description='Event manager and behavior for hover events',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    author='Filip Radovic',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='Kivy kivy-garden',
    packages=find_namespace_packages(include=['kivy_garden.*']),
    install_requires=[],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
    project_urls={
        'Bug Reports': URL + '/issues',
        'Source': URL,
    },
)