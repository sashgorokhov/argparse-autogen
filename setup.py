from distutils.core import setup

with open('README.md') as readme:
    with open('HISTORY.md') as history:
        long_description = readme.read() + '\n\n' + history.read()

VERSION = '1.0'

setup(
    name='argparse-autogen',
    py_modules=['argparse_autogen'],
    version=VERSION,
    url='https://github.com/sashgorokhov/argparse-autogen',
    download_url='https://github.com/sashgorokhov/argparse-autogen/archive/v%s.zip' % VERSION,
    keywords=['python', 'argparse', 'generate'],
    classifiers=[],
    long_description=long_description,
    license='MIT License',
    author='sashgorokhov',
    author_email='sashgorokhov@gmail.com',
    description="Parser with automatic creation of parsers and subparsers for paths.",
)
