import re
from functools import partial

import setuptools


requires = [
    'Click>=7.0,<8.0',
    'docker>=3.7.0,<3.8.0',
]

scripts = [
    'bin/pydockenv',
]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: Unix',
    'Programming Language :: Unix Shell',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development',
    'Topic :: Utilities'
]

with open('README.md', 'r') as fh:
    long_description = fh.read()


def get_about():
    regexes = {
        'title': r"^__title__\s=\s(?P<quote>['])(?P<title>\w*)(?P=quote)$",
        'version': r"^__version__\s=\s(?P<quote>['])(?P<version>[\d\.]*)(?P=quote)$",
        'author': r"^__author__\s=\s(?P<quote>['])(?P<author>[\w\s]*)(?P=quote)$",
        'author_email': r"^__author_email__\s=\s(?P<quote>['])(?P<author_email>.*)(?P=quote)$",
        'description': r"^__description__\s=\s(?P<quote>['])(?P<description>.*)(?P=quote)$",
        'project_url': r"^__project_url__\s=\s(?P<quote>['])(?P<project_url>.*)(?P=quote)$",
    }

    with open('./pydockenv/__init__.py') as f:
        raw_about = f.read()

    extract = partial(re.search, string=raw_about, flags=re.MULTILINE)
    return {k: extract(v).group(k) for k, v in regexes.items()}


about = get_about()


setuptools.setup(
    name=about['title'],
    version=about['version'],
    author=about['author'],
    author_email=about['author_email'],
    description=about['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=about['project_url'],
    packages=setuptools.find_packages(exclude=['tests']),
    scripts=scripts,
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    classifiers=classifiers,
)
