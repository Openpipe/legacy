#  import pytest
from mdatapipe.client.testing import TestRun
from glob import glob
from os.path import join
import os
#  import platform
#  import pytest

test_file = os.environ.get("TEST_FILE")
if test_file:
    test_files_list = [test_file]
else:
    plugin_list_mask = join("tests", "plugins", "*", "*", "*.yaml")
    test_files_list = [item for item in glob(plugin_list_mask) if 'asserting' not in item]


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    #  os_system = platform.system()
    for test_file in metafunc.cls.test_files:
        idlist.append(test_file)
        argnames = ["test_filename"]
        argvalues.append(([test_file]))
        # if os_system != 'Windows' and 'command' in test_file:
        #    argnames.append("conf")
        #    argvalues.append(([pytest.skip("Smoke tests must....")]))

    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")

# if os_system != 'Windows' and test_file in WIN_ONLY:
#     argnames.append("conf")
#     argvalues.append(pytest.skip("Smoke tests must...."))


class TestPipeline(object):
    test_files = test_files_list

    def test(self, test_filename):
        exit_code, exit_message = TestRun(test_filename)
        print(exit_code, exit_message)
        if exit_code != 0:
            raise Exception(exit_message)
