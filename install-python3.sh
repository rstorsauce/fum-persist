#!/bin/sh

cd python3

python3 setup.py sdist

pip install dist/fumpersist-0.0.1.tar.gz
