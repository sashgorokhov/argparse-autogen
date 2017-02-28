import argparse
from unittest import TestCase, mock

import pytest

import argparse_autogen


@pytest.fixture
def parser():
    return argparse_autogen.EndpointParser()


class BaseTestCase(TestCase):
    def setUp(self):
        self.parser = parser()


class TestClearInternalKeys(BaseTestCase):
    def test_namespace_conversion(self):
        args = self.parser.clear_internal_keys(argparse.Namespace())
        assert isinstance(args, dict)

    def test_internal_keys_deleted(self):
        args = {i: i for i in self.parser.internal_keys}
        cleaned_args = self.parser.clear_internal_keys(args)

        for key in args:
            assert key not in cleaned_args

    def test_kwargs_keys(self):
        args = {'kwargs': ['foo=bar']}
        cleaned_args = self.parser.clear_internal_keys(args)

        assert 'kwargs' in cleaned_args
        assert 'foo' in cleaned_args['kwargs']
        assert cleaned_args['kwargs']['foo'] == 'bar'


class TestGetEndpointParser(BaseTestCase):
    def test_path_split_by_dot(self):
        path = 'test.foo.bar'
        parser = self.parser.get_endpoint_parser(path)
        assert parser.path == ['test', 'foo', 'bar']

    def test_path_split_by_space(self):
        path = 'test foo bar'
        parser = self.parser.get_endpoint_parser(path)
        assert parser.path == ['test', 'foo', 'bar']

    def test_empty_path(self):
        assert self.parser.get_endpoint_parser('') is self.parser

    def test_subparsers_added(self):
        path = 'test foo bar'
        assert self.parser.subparsers is None
        parser = self.parser.get_endpoint_parser(path)
        assert self.parser.subparsers is not None

    def test_parsers_path(self):
        path = ['test', 'foo', 'bar']

        self.parser.get_endpoint_parser(path)
        parser = self.parser

        for item in path:
            assert item in parser.subparsers._name_parser_map
            parser = parser.subparsers._name_parser_map[item]


class TestAddEndpoint(BaseTestCase):
    def test_parser_defaults(self):
        path = 'test.foo.bar'

        parser = self.parser.add_endpoint(path, func=lambda foo: print(foo))

        assert '__func__' in parser._defaults
        assert '__endpoint__' in parser._defaults


class TestEndpointParser(BaseTestCase):
    def test_endpoint_parsing(self):
        func = mock.Mock()
        self.parser.add_endpoint('list.dir', func=func)

        args = self.parser.parse_args(['list', 'dir'])
        assert args.__endpoint__ == 'list.dir'

        self.parser.call(args)

        func.assert_any_call()

    def test_several_endpoints(self):
        func1 = mock.Mock()
        func2 = mock.Mock()

        self.parser.add_endpoint('list.dir', func=func1)
        self.parser.add_endpoint('list.files', func=func2)

        self.parser.parse_and_call(['list', 'dir'])
        func1.assert_any_call()

        self.parser.parse_and_call(['list', 'files'])
        func2.assert_any_call()

    def test_invalid_endpoint(self):
        self.parser.add_endpoint('list.dir')

        with self.assertRaises(SystemExit):
            self.parser.parse_and_call(['list'])


class TestGetFuncArguments(BaseTestCase):
    def test_get_func_arguments(self):
        def foo(foo, bar):
            pass

        args = {'foo': 1, 'bar': 2, 'baz': 3}
        kwargs = self.parser.get_func_arguments(foo, args)

        assert 'foo' in kwargs
        assert 'bar' in kwargs
        assert 'baz' not in kwargs

    def test_with_kwargs(self):
        def foo(foo, bar, **kwargs):
            pass

        args = argparse.Namespace(foo=1, bar=2, baz=3, kwargs=dict(hello='world'))

        kwargs = self.parser.get_func_arguments(foo, args)

        assert 'foo' in kwargs
        assert 'bar' in kwargs
        assert 'baz' not in kwargs
        assert 'hello' in kwargs
        assert kwargs['hello'] == 'world'
        assert 'kwargs' not in kwargs