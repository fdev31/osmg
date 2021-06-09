from setuptools import setup, find_packages

def getdesc():
    try:
        open('../README.md').read()
    except IOError:
        return 'N/A'

setup(
    name="back",
    version="0.0.0",
    author="Fabien Devaux & Jean Olivier Menoube",
    license="proprietary",
    description="Our awesome game",
    long_description=getdesc(),
    install_requires=[
        'aiofiles>=0.7.0',
#        'fastapi-plugins==0.8.1',
        'aiojobs>=0.3.0',
        'ujson',
        'orjson',
        'sse-starlette>=0.7.2',
        'hiredis',
        'aioredis',
        'fastapi==0.65.1',
        'uvicorn==0.13.4',
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

