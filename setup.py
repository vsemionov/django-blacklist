import os

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


setup(
    name='django-blacklist',

    version='0.1.0',

    description='Blacklist users and hosts in Django. Automatically blacklist rate-limited clients.',
    long_description=README,

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

    packages=find_packages(),

    install_requires=[
        'Django'
    ]
)
