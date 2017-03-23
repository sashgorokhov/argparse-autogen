import argparse_autogen


def test_parser_description(parser):
    def foo():
        """
        Hello, world!

        :return:
        """
        pass

    argparse_autogen.autospec(parser, foo)
    assert parser.description == 'Hello, world!'


def test_cls_method(parser):
    class Foo:
        def bar(self):
            pass

        @classmethod
        def foo(cls, what):
            pass

    foo = Foo()

    argparse_autogen.autospec(parser, foo.bar)
    parser.add_argument.assert_not_called()

    argparse_autogen.autospec(parser, foo.foo)
    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('what',)


def test_param_no_docstring(parser):
    def foo(bar):
        pass

    argparse_autogen.autospec(parser, foo)

    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('bar',)
    assert parser.add_argument.call_args_list[0][1]['help'] == 'bar'


def test_param_docstring(parser):
    def foo(bar):
        """
        :param str bar: this is help
        :return:
        """
        pass

    argparse_autogen.autospec(parser, foo)

    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('bar',)
    assert parser.add_argument.call_args_list[0][1]['help'] == 'this is help'


def test_positional_params(parser):
    def foo(*args):
        pass

    argparse_autogen.autospec(parser, foo)
    parser.add_argument.assert_not_called()


def test_keyword_param(parser):
    def foo(**kwargs):
        pass

    argparse_autogen.autospec(parser, foo)

    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('kwargs',)
    assert parser.add_argument.call_args_list[0][1]['nargs'] == '*'
    assert parser.add_argument.call_args_list[0][1]['help'] != 'kwargs'


def test_keyword_param_with_docstring(parser):
    def foo(**kwargs):
        """
        :param kwargs: this is help
        """

    argparse_autogen.autospec(parser, foo)

    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('kwargs',)
    assert parser.add_argument.call_args_list[0][1]['help'] == 'this is help'


def test_param_default(parser):
    def foo(bar='baz'):
        pass

    argparse_autogen.autospec(parser, foo)

    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('--bar',)
    assert parser.add_argument.call_args_list[0][1]['default'] == 'baz'


def test_param_default_bool(parser):
    def foo(bar=True):
        pass

    argparse_autogen.autospec(parser, foo)

    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('--bar',)
    assert parser.add_argument.call_args_list[0][1]['default']
    assert parser.add_argument.call_args_list[0][1]['action'] == 'store_false'

    def foo(bar=False):
        pass

    argparse_autogen.autospec(parser, foo)

    assert parser.add_argument.call_args_list[1][0] == ('--bar',)
    assert not parser.add_argument.call_args_list[1][1]['default']
    assert parser.add_argument.call_args_list[1][1]['action'] == 'store_true'


def test_argument_overrides(parser):
    def foo(bar):
        """
        :param bar: this is help
        """
        pass

    argparse_autogen.autospec(parser, foo, argument_overrides={'bar': {'help': 'my own help'}})

    assert parser.add_argument.called
    assert parser.add_argument.call_args_list[0][0] == ('bar',)
    assert parser.add_argument.call_args_list[0][1]['help'] == 'my own help'
