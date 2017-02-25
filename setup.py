from distutils.core import setup

with open('README.md') as readme:
    with open('HISTORY.md') as history:
        long_description = readme.read() + '\n\n' + history.read()

setup(
    name='argparse-autogen',
    py_modules=['argparse_autogen'],
    version='0.1',
    url='https://github.com/sashgorokhov/argparse-autogen',
    download_url='https://github.com/sashgorokhov/argparse-autogen/archive/master.zip',
    keywords=['python', 'argparse', 'generate'],
    classifiers=[],
    long_description=long_description,
    license='MIT License',
    author='sashgorokhov',
    author_email='sashgorokhov@gmail.com',
    description="Parser with automatic creation of parsers and subparsers for paths.",
)
