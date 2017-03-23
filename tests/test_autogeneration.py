from unittest import mock

import pytest

import argparse_autogen


@pytest.fixture
def mock_obj():
    parent_mock = mock.Mock()
    child_mock = mock.Mock()

    class Parent:
        def parent(self):
            parent_mock()

    class Child(Parent):
        def __init__(self):
            self.parent_mock = parent_mock
            self.child_mock = child_mock
            self.bar = self.Bar()

        def parent(self):
            child_mock()

        def child(self):
            pass

        class Bar():
            def bar(self):
                pass

    return Child()


@pytest.mark.parametrize(['root_path'], [
    [None],
    [('root',)],
    [tuple()],
    [list()],
])
def test_get_cls_paths(root_path, mock_obj):
    paths = argparse_autogen._get_cls_paths(mock_obj, path=root_path)

    get_path = lambda name: (root_path or tuple()) + (name,)

    assert get_path('child') in paths
    assert get_path('parent') in paths
    assert get_path('bar') not in paths

    assert paths[get_path('parent')].__self__ == mock_obj
    paths[get_path('parent')]()
    assert not mock_obj.parent_mock.called and mock_obj.child_mock.called


@pytest.mark.parametrize(['root_path'], [
    [None],
    [('root',)],
])
def test_generate_endpoints(root_path, parser: argparse_autogen.EndpointParser, mock_obj):
    get_path = lambda name: (root_path or tuple()) + (name,)

    parser.generate_endpoints(mock_obj, root_path=root_path)

    parser.parse_and_call(get_path('parent'))
    assert mock_obj.child_mock.called
