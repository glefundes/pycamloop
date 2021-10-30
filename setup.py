import os
import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
REQS = HERE / "requirements.txt"

install_requires = []
if os.path.isfile(REQS):
    with open(REQS) as f:
        install_requires = f.read().splitlines()

setuptools.setup(
    name="pycamloop",
    version="0.0.2",
    description="Forget the boilerplate from OpenCV camera loops and get to coding the interesting stuff",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/glefundes/pycamloop",
    author="Gabriel Lefundes",
    author_email="lefundes.gabriel@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=install_requires,
)
