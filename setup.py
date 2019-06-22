import os

from setuptools import setup, find_packages

import blacklist


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

packages = find_packages()
packages.extend(['blacklist.management', 'blacklist.management.commands'])


setup(
    name='django-blacklist',

    version=blacklist.__version__,

    description='Blacklist users and hosts in Django. Automatically blacklist rate-limited clients.',
    long_description=README,
    long_description_content_type='text/markdown',

    url='https://github.com/vsemionov/django-blacklist',

    author='Victor Semionov',
    author_email='vsemionov@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security'
    ],

    keywords='django blacklist ratelimit firewall',

    packages=packages,

    install_requires=[
        'Django'
    ]
)
