from setuptools import find_packages, setup


setup(
    name='pynello',
    version='1.0',
    license='GPL3',
    description='Python library for nello.io locks',
    long_description=open('README.rst').read(),
    author='Philipp Schmitt',
    author_email='philipp@schmitt.co',
    url='https://github.com/pschmitt/pynello',
    packages=find_packages(),
    install_requires=['requests'],
)
