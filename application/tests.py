# coding=utf-8
import optparse
import os
import sys
import unittest2

USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to the SDK installation
TEST_PATH   Path to package containing test modules"""


def main(sdk_path, test_path):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest2.loader.TestLoader().discover(test_path)
    unittest2.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    parser = optparse.OptionParser(USAGE)
    options, args = parser.parse_args()
    if len(args) != 2:
        SDK_PATH = os.path.join(os.path.abspath('.'), '../../google_appengine')
        TEST_PATH = os.path.join(os.path.abspath('.'), 'tests')
    else:
        SDK_PATH = args[0]
        TEST_PATH = args[1]
    main(SDK_PATH, TEST_PATH)
