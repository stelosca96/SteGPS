import setuptools
import re

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('steGPS/__init__.py', 'r') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        f.read(), re.MULTILINE).group(1)

setuptools.setup(
    name='SteGPS',
    version=version,
    author='Stefano Loscalzo',
    author_email='stefano.loscalzo@gmail,com',
    description='BN-200 GPS python library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/stelosca96/SteGPS',
    packages=['steGPS'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.6',
)
