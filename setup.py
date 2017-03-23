from distutils.core import setup

with open('README.md') as readme:
    with open('HISTORY.md') as history:
        long_description = readme.read() + '\n\n' + history.read()

try:
    import pypandoc

    long_description = pypandoc.convert(long_description, 'rst', 'markdown')
except(IOError, ImportError):
    long_description = long_description

VERSION = '1.3.3'

setup(
    name='argparse-autogen',
    py_modules=['argparse_autogen'],
    version=VERSION,
    url='https://github.com/sashgorokhov/argparse-autogen',
    download_url='https://github.com/sashgorokhov/argparse-autogen/archive/v%s.zip' % VERSION,
    keywords=['python', 'argparse', 'generate'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals',
    ],
    long_description=long_description,
    license='MIT License',
    author='sashgorokhov',
    author_email='sashgorokhov@gmail.com',
    description="Parser with automatic creation of parsers and subparsers for paths.",
)
