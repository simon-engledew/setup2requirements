# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='setup2requirements',
    description='Generate requirements.txt from setup.py files.',
    version='0.1.0',
    author='Simon Engledew',
    author_email='simon.engledew@gmail.com',
    url='https://github.com/simon-engledew/setup2requirements',
    packages=['setup2requirements'],
        entry_points={
        'console_scripts': [
            'setup2requirements = setup2requirements.__main__:main',
        ]
    },
    install_requires=[
    ],
    license='MIT',
    zip_safe=True,
    classifiers=[
    ],
)
