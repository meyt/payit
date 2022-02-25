from setuptools import setup, find_packages


def read_version(module_name):
    from re import match, S
    from os.path import join, dirname

    with open(join(dirname(__file__), module_name, "__init__.py")) as f:
        return match(r".*__version__.*('|\")(.*?)('|\")", f.read(), S).group(2)


package_name = "payit"
dependencies = ["zeep >= 3.4.0", "requests >= 2.22.0", "py3rijndael >= 0.3.0"]

setup(
    name=package_name,
    version=read_version(package_name),
    author="Mahdi Ghanea.g",
    description="Online payment gateways wrapper library.",
    long_description=open("README.rst").read(),
    url="https://github.com/meyt/payit",
    packages=find_packages(),
    install_requires=dependencies,
    license="MIT License",
    classifiers=[
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
