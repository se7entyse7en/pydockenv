import json

import setuptools
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


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
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Utilities',
]

with open('README.md', 'r') as fin:
    long_description = fin.read()


with open('meta.json') as fin:
    about = json.load(fin)


class bdist_wheel(_bdist_wheel):

    def finalize_options(self):
        _bdist_wheel.finalize_options(self)
        self.root_is_pure = False

    def get_tag(self):
        if not self.plat_name_supplied:
            raise ValueError('plat_name is required')

        return 'py2.py3', 'none', self.plat_name


setuptools.setup(
    name=about['title'],
    version=about['version'],
    author=about['author'],
    author_email=about['author_email'],
    description=about['description'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=about['project_url'],
    packages=setuptools.find_packages(),
    scripts=scripts,
    package_data={
        '': ['LICENSE'],
    },
    data_files=[('bin', ['bin/pydockenv_exec'])],
    include_package_data=True,
    classifiers=classifiers,
    cmdclass={
        'bdist_wheel': bdist_wheel,
    },
)
