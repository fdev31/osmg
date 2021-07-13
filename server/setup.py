import os
from setuptools import setup, find_packages

deps = [l.strip() for l in open('required.txt', encoding='utf-8').readlines()]

def getdesc():
    try:
        open('../README.md').read()
    except IOError:
        return 'N/A'

setup(
    name="back",
    version="0.1.0",
    author="Fabien Devaux & Jean Olivier Menoube",
    license="proprietary",
    description="Our awesome game",
    long_description=getdesc(),
    install_requires=deps,
    scripts=['back-start'],
    packages=find_packages(),
    url='https://github.com/jomenoube60/our-awesome-game',
    zip_safe=True,
    classifiers=[
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
    ]
)

