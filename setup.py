import pathlib

from setuptools import find_packages, setup

long_description = (pathlib.Path(__file__).parent.resolve() / "README.md").read_text()

setup(
    name="paranoid-deobfuscator",
    packages=find_packages(),
    version="2.0.0",
    license="Apache 2.0",
    author="Giacomo Ferretti",
    author_email="giacomo.ferretti.00@gmail.com",
    description='Deobfuscate "paranoid" protected apps',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/giacomoferretti/paranoid-deobfuscator",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Disassemblers",
    ],
    install_requires=[
        "numpy",
    ],
)
