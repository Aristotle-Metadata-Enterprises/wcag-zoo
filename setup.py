import os
from setuptools import setup, find_packages

import wcag_zoo
VERSION = wcag_zoo.version

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='wcag-zoo',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    license='',
    description='',
    long_description=README,
    url='https://github.com/data61/wcag-zoo',
    author='Samuel Spencer',
    author_email='sam@aristotlemetadata.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Environment :: Web Environment',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
    ],
    entry_points={
        'console_scripts': [
            'zookeeper = wcag_zoo.zookeeper:zookeeper',
        ],
    },
    install_requires=[
        "lxml",
        "premailer",
        "webcolors",
        "click",
        "xtermcolor",
    ],

)
