#  import pytest
from mdatapipe.client.testing import TestRun
from glob import glob
from os.path import join


plugin_list_mask = join("tests", "plugins", "test", "asserting", "*.yaml")
test_files_list = glob(plugin_list_mask)


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for test_file in metafunc.cls.test_files:
        idlist.append(test_file)
        argnames = ["test_filename"]
        argvalues.append(([test_file]))
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestAssert(object):
    """ Validates that the assert plugin produces an error """
    test_files = test_files_list

    def test(self, test_filename):
        try:
            assert TestRun(test_filename)
        except AssertionError:
            pass
        else:
            raise("AssertionError not raised when it should")
