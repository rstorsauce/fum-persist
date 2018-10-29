#!/bin/sh

cd python3

# TODO: get this out of the shell script and into a proper pip dependency
pip3 install uuid

python3 setup.py sdist

pip3 install dist/fum-persist-0.0.1.tar.gz
