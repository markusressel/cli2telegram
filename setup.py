#  Copyright (c) 2019 Markus Ressel
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#

from setuptools import setup, find_packages

VERSION_NUMBER = "1.1.2"

DEVELOPMENT_STATUS = "Development Status :: 5 - Production/Stable"
VERSION_NAME = VERSION_NUMBER


def readme_type() -> str:
    import os
    if os.path.exists("README.rst"):
        return "text/x-rst"
    if os.path.exists("README.md"):
        return "text/markdown"


def readme() -> [str]:
    if readme_type() == "text/markdown":
        file_name = "README.md"
    else:
        file_name = "README.rst"

    with open(file_name) as f:
        return f.read()


def install_requirements() -> [str]:
    return read_requirements_file("requirements.txt")


def test_requirements() -> [str]:
    return read_requirements_file("test_requirements.txt")


def read_requirements_file(file_name: str):
    with open(file_name, encoding='utf-8') as f:
        requirements_file = f.readlines()
    return [r.strip() for r in requirements_file]


setup(
    name='cli2telegram',
    version=VERSION_NAME,
    description='Small utility to send Telegram messages from the CLI.',
    long_description=readme(),
    long_description_content_type=readme_type(),
    license='AGPLv3+',
    author='Markus Ressel',
    author_email='mail@markusressel.de',
    url='https://github.com/markusressel/cli2telegram',
    packages=find_packages(),
    classifiers=[
        DEVELOPMENT_STATUS,
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=install_requirements(),
    tests_require=test_requirements(),
    entry_points={
        'console_scripts': ['cli2telegram = cli2telegram.cli:cli']
    }
)
