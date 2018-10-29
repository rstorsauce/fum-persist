import os

from setuptools import setup, find_packages

import fum

ROOT = os.path.abspath(os.path.dirname(__file__))

setup(
    name='fum-persist',
    version=fum.__version__,
    description="persistence library for fum",
    long_description="persistence library for fum",
    keywords='alfredo python sdk',
    url='https://github.com/rstorsauce/fum_persist',
    license='MIT',
    author='RStor, Inc.',
    author_email='isaac@rstor.io',
    packages=find_packages(exclude=['docs*', 'tests*', 'examples*']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
