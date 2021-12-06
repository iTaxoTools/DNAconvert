"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='DNAconvert',

    version='0.1.dev1',

    description='Converts between genetic formats',

    long_description=long_description,

    long_description_content_type='text/markdown',

    url='https://github.com/iTaxoTools/DNAconvert/',

    author='Vladimir Kharchev',

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    package_dir={'': 'src'},

    packages=find_namespace_packages(
        # exclude=('itaxotools.common*',),
        include=('itaxotools*',),
        where='src',
    ),

    python_requires='>=3.8, <4',

    install_requires=[
        'python-nexus',
        'appdirs',
    ],

    extras_require={
        'dev': ['pyinstaller'],
    },

    # Include all data from MANIFEST.in
    include_package_data=True,

    entry_points={
        'console_scripts': [
            'DNAconvert=itaxotools.DNAconvert:main',
        ],
        'pyinstaller40': [
            'hook-dirs = itaxotools.__pyinstaller.DNAconvert:get_hook_dirs',
            'tests = itaxotools.__pyinstaller.DNAconvert:get_pyinstaller_tests'
        ]
    },

)
