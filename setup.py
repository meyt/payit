import re
import os.path
import sys

from setuptools import setup, find_packages

package_name = 'payit'

# reading package's version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), package_name, '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

dependencies = [
    'zeep >= 3.4.0',
    'requests >= 2.22.0',
    'py3rijndael >= 0.3.0'
]

setup(
    name=package_name,
    version=package_version,
    author='Mahdi Ghanea.g',
    description='Online payment gateways wrapper library.',
    long_description=open('README.rst').read(),
    url='https://github.com/meyt/payit',
    packages=find_packages(),
    install_requires=dependencies,
    license='MIT License',
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
