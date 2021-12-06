"""Convert between different file formats containing genetic information."""

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='DNAconvert',
    version='0.2.0',
    description='Converts between genetic formats',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/iTaxoTools/DNAconvert/',
    author='Vladimir Kharchev',
    package_dir={'': 'src'},
    packages=find_namespace_packages(
        include=('itaxotools*',),
        where='src',
    ),
    python_requires='>=3.8.6, <4',
    install_requires=[
        'python-nexus',
        'appdirs',
    ],
    extras_require={
        'dev': ['pyinstaller'],
    },
    entry_points={
        'console_scripts': [
            'DNAconvert=itaxotools.DNAconvert:main',
        ],
        'pyinstaller40': [
            'hook-dirs = itaxotools.__pyinstaller.DNAconvert:get_hook_dirs',
            'tests = itaxotools.__pyinstaller.DNAconvert:get_pyinstaller_tests'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    include_package_data=True,
)
