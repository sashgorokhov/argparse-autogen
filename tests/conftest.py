from unittest import mock

import pytest

import argparse_autogen


@pytest.fixture
def parser():
    parser = argparse_autogen.EndpointParser()
    parser.add_argument = mock.Mock()
    return parser
