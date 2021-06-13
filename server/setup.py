from setuptools import setup, find_packages

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
    install_requires=[
        'aiofiles>=0.7.0',
        'aiojobs>=0.3.0',
        'arq >= 0.20.0',
        'orjson>=3.5.3',
        'sse-starlette>=0.7.2',
        'hiredis==2.0.*',
        'aioredis>=2.0.0a1',
        'fastapi==0.65.*',
        'uvicorn>=0.13.0',
        ],
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

