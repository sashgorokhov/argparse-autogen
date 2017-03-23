# argparse-autogen

[![PyPI](https://img.shields.io/pypi/status/argparse-autogen.svg)](https://github.com/sashgorokhov/argparse-autogen) [![PyPI](https://img.shields.io/pypi/pyversions/argparse-autogen.svg)](https://github.com/sashgorokhov/argparse-autogen) [![PyPI version](https://badge.fury.io/py/argparse-autogen.svg)](https://badge.fury.io/py/argparse-autogen) [![GitHub release](https://img.shields.io/github/release/sashgorokhov/argparse-autogen.svg)](https://github.com/sashgorokhov/argparse-autogen) [![Build Status](https://travis-ci.org/sashgorokhov/argparse-autogen.svg?branch=master)](https://travis-ci.org/sashgorokhov/argparse-autogen) [![codecov](https://codecov.io/gh/sashgorokhov/argparse-autogen/branch/master/graph/badge.svg)](https://codecov.io/gh/sashgorokhov/argparse-autogen) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/sashgorokhov/argparse-autogen/master/LICENSE)

Parser with automatic creation of parsers and subparsers for paths.

## Installation

Supported versions of python: **`3.3+`** (because of inspect.Signature, which was introduced in python 3.3)

```shell
pip install argparse-autogen
```

## Usage

`argparse_autogen.EndpointParser` is intended to replace basic `argparse.ArgumentParser`. It extends subparsers creation logic, and adds a new special method `add_endpoint`.

Simple example:
```python
import argparse_autogen

class MyCli():
  def do_stuff(self, target, force=False):
    """
    This does cool stuff!
    
    :param str target: Target to execute a cool stuff
    :param bool force: Force doing cool stuff
    """
    print(target, force)

cli = MyCli()

parser = argparse_autogen.EndpointParser()
parser.add_endpoint('do_stuff', cli.do_stuff)
parser.parse_and_call(['do_stuff', 'my target']) # this will print "my target false"
parser.parse_and_call(['do_stuff', '--force', 'my target']) # this will print "my target true"
```

`add_endpoint` method is clever enough to parse methods docstring and add corresponding helps in arguments. For example, 
`parser.parse_args(['do_stuff', '--help'])` in above example will show something like
```
usage: example.py do_stuff [-h] [--force]

This does cool stuff!

optional arguments:
  -h, --help  show this help message and exit
  --force     Force doing cool stuff
```
This magic is done by `argparse_autogen.autospec` function. It introspects function signature, and adds corresponding argparse arguments to parser. `**kwargs` are supported and can be passed as `[key=value [key=value ...]]`. You can override argument settings by passing `argument_overrides` option to `add_endpoint`. This must be a `dict[str, dict]` where keys are parameter name, and values are parameters to override defaults passed to `parser.add_argument`

## More endpoint examples

Nested class and complex paths:
```python
import argparse_autogen

class MyCli():
  def __init__(self):
    self.users = self.Users()
    self.groups = self.Groups()
  
  class Users():
    def get(self, user_id): pass
    def list(self, **filter): pass
    def set_roles(self, user_id, *role): pass
    def update(self, user_id, **fields): pass
   
  class Groups():
    def get(self, group_id): pass

cli = MyCli()

parser = argparse_autogen.EndpointParser()

parser.add_endpoint('users.get', cli.users.get, argument_overrides={'user_id': {'help': 'Users id'}})
parser.add_endpoint('users.list', cli.users.list)
parser.add_endpoint(cli.users.update) 
# this will use __qualname__ of update func as path, lowercased and trailing and ending underscores removed.
# The first item of qualname is skipped, so it would be `users.update`, not `mycli.users.update`

# Alternatively, you can use autogeneration of paths and endpoints:
# parser.generate_endpoints(cli.users, root_path='users', endpoint_kwargs={'users.get': {'argument_overrides': {'user_id': {'help': 'Users id'}}}})
# Will create endpoints from class methods.

groups_get_parser = parser.add_endpoint('groups get', cli.groups.get, autospec=False)
groups_get_parser.add_argument('group_id', help='Group id')

users_parser = parser.get_endpoint_parser('users')
users_parser.description = 'Users operations'

parser.parse_and_call()
```
