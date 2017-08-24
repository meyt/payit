from setuptools import setup, find_packages
import os.path
import re

package_name = 'pyment'

# reading package's version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), package_name, '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

dependencies = [
  'zeep',
]

setup(
    name=package_name,
    version=package_version,
    author='Mahdi Ghane.g',
    description='A very micro http framework.',
    long_description=open('README.rst').read(),
    url='https://github.com/meyt/pyment',
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
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
