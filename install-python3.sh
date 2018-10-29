#!/bin/sh

cd python3

python3 setup.py sdist

# TODO: get this out of the shell script and into a proper pip dependency
pip install uuid
pip install dist/fum-persist-0.0.1.tar.gz
