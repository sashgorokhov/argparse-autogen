import argparse_autogen


def test_singleline_description():
    docstring = """Hello, world!"""

    description, params = argparse_autogen.parse_docstring(docstring)

    assert params == []
    assert description == docstring


def test_multiline_description():
    docstring = """
    Hello, world!
    Hello, world!
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert params == []
    assert description == 'Hello, world!\nHello, world!'


def test_spaced_multiline_description():
    docstring = """
    Hello, world!

    Hello, world!

    What?
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert params == []
    assert description == 'Hello, world!\nHello, world!\nWhat?'


def test_simple_params():
    docstring = """
    Hello, world!

    :param str foo: this is help
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert description == 'Hello, world!'
    assert len(params) == 1
    assert params[0]['type'] == 'str'
    assert params[0]['name'] == 'foo'
    assert params[0]['description'] == 'this is help'


def test_param_without_description():
    docstring = """
    Hello, world!

    :param str foo:
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert len(params) == 1
    assert params[0]['description'] is None


def test_multiple_params():
    docstring = """
    Hello, world!

    :param str foo: this is help
    :param int bar: no help
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert description == 'Hello, world!'
    assert len(params) == 2

    assert params[0]['type'] == 'str'
    assert params[0]['name'] == 'foo'
    assert params[0]['description'] == 'this is help'

    assert params[1]['type'] == 'int'
    assert params[1]['name'] == 'bar'
    assert params[1]['description'] == 'no help'


def test_multiline_param_description():
    docstring = """
    Hello, world!

    :param str foo: this is help
        and it is multiline
    :param int bar: no help
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert params[0]['description'] == 'this is help\nand it is multiline'
    assert params[1]['description'] == 'no help'


def test_unknown_param():
    docstring = """
    Hello, world!

    :param str foo: this is help
    :raises ValueError:
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert len(params) == 1
    assert params[0]['type'] == 'str'
    assert params[0]['name'] == 'foo'
    assert params[0]['description'] == 'this is help'


def test_no_description():
    docstring = """
    :param str foo: this is help
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert description == ''
    assert len(params) == 1


def test_param_no_type():
    docstring = """
    :param foo: this is help
    """

    description, params = argparse_autogen.parse_docstring(docstring)

    assert len(params) == 1
    assert params[0]['type'] is None
    assert params[0]['name'] == 'foo'
    assert params[0]['description'] == 'this is help'
