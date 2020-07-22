
import os.path
import re
from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()

requirements = []
with open('requirements.txt') as f:
    for line in f.readlines():
        line.strip()
        if line.startswith('#'):
            continue
        requirements.append(line)


version = None
with open(os.path.join('flask_mdict', '__init__.py')) as f:
    text = f.read()
    mo = re.search(r"__version__ = '([\d\.]+)'", text)
    version = mo.group(1)


setup(
    name='flask_mdict',
    version=version,
    author='Yugang LIU',
    author_email='liuyug@gmail.com',
    url='https://github.com/liuyug/flask-mdict',
    license='MIT',
    description='Flask Mdict Server',
    long_description=long_description,
    python_requires='>=3.6',
    platforms=['noarch'],
    py_modules=['flask_mdict'],
    install_requires=requirements,
    zip_safe=False,
)
