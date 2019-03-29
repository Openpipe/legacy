from mdatapipe.client.testing import TestRun
from os.path import join


def pytest_generate_tests(metafunc):
    idlist = []
    argvalues = []
    for test_file in metafunc.cls.test_files:
        idlist.append(test_file)
        argnames = ["test_filename"]
        argvalues.append(([test_file]))
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


class TestDynamicConfig(object):
    test_files = [join("tests", "dynaconf.yaml")]

    def test(self, test_filename):
        exit_code, exit_message = TestRun(test_filename)
        print(exit_code, exit_message)
        if exit_code != 0:
            raise Exception(exit_message)
