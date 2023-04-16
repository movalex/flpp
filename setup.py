from setuptools import setup
from os import path

cur_dir = path.abspath(path.dirname(__file__))
with open(path.join(cur_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='FLPP',
    description='FLPP is a simple lua-python data structures parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.3.0',
    author='SirAnthony, Alexey Bogomolov',
    url='https://github.com/movalex/flpp',
    license='MIT',
    keywords=['lua'],
    py_modules=['flpp'],
    python_requires='>3.6'
)
