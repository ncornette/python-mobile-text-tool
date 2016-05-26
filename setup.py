#!/usr/bin/env python
from os import path

from setuptools import setup
from pip.req import parse_requirements
import codecs

install_reqs = parse_requirements('./requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codecs.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='Mobile-Text-Tool',
      version='1.1.2',
      description='Tools for editing translations in mobile apps',
      license='MIT',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
      ],
      keywords='translations mobile development',
      long_description=long_description,
      author='Nicolas Cornette',
      author_email='nicolas.cornette@gmail.com',
      install_requires=reqs,
      url='https://github.com/ncornette/python-mobile-text-tool',
      packages=['mobileStrings'],
      py_modules=['update_wordings'],
      entry_points={
          'console_scripts': [
              'update_wordings = update_wordings:main'
          ]
      }
      )
