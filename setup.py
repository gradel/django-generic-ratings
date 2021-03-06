from setuptools import setup
import os

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

data_files = []
for dirpath, dirnames, filenames in os.walk('ratings'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath[len("ratings") + 1:], f))

version = "%s.%s" % __import__('ratings').VERSION[:2]

install_requires = open('requirements.txt').read().splitlines()

dev_requires = [
    'flake8',
]

setup(name='django-generic-ratings',
    version=version,
    description='Django ratings tools supporting ajax, generic content type scores, multiple ratings for each content object.',
    author='Francesco Banconi',
    author_email='francesco.banconi@gmail.com',
    url='https://bitbucket.org/frankban/django-generic-ratings/',
    packages=[
        'ratings',
        'ratings.templatetags',
        'ratings.views',
        'ratings.forms',
        'ratings.management',
        'ratings.management.commands',
    ],
    package_data={'ratings': data_files},
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities'
    ],
    test_suite='ratings.tests.runtests.runtests',
)
