#!/usr/bin/env python
from setuptools import setup

# Put here required packages or
# Uncomment one or more lines below in the install_requires section
# for the specific client drivers/modules your application needs.
packages = ['tornado']

setup(name='anonymous web chat', version='1.0',
      description='chat with people whose you do not know',
      author='Davidenko Konstantyn', author_email='kostya_ya@mail.ru',
      url='kostya_ya@mail.ru',
      install_requires=packages,
     )
