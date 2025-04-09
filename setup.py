
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


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('flask_mdict/static')
extra_files += package_files('flask_mdict/templates')
extra_files += package_files('flask_mdict/plugins')


setup(
    name='flask_mdict',
    version=version,
    author='Yugang LIU',
    author_email='liuyug@gmail.com',
    url='https://github.com/liuyug/flask-mdict',
    license='MIT',
    description='Flask Mdict Server',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # long_description_content_type="text/markdown",
    python_requires='>=3.6',
    platforms=['noarch'],
    packages=find_packages(),
    package_data={'': extra_files},
    install_requires=requirements,
    zip_safe=False,
)
