import os
import sys
import unittest
from io import StringIO
from typing import Optional, TextIO, List, NamedTuple

import requests
from dict_compare import compare_dicts
from jsonasobj import loads as jao_loads
from pyjsg.jsglib.loader import loads as jsg_loads, is_valid

from ShExJSG import ShExJ


# Repository to validate against
shexTestRepository = "https://api.github.com/repos/shexSpec/shexTest/contents/schemas"


# TODO: consider a
# shexTestRepository = os.path.abspath(os.path.expanduser("~/git/shexSpec/shexTest/schemas/"))

# If not empty, validate this single file
shexTestJson: str = None
# shexTestJson = "https://raw.githubusercontent.com/shexSpec/shexTest/2.0/schemas/" \
#                "1refbnode_with_spanning_PN_CHARS_BASE1.json"


STOP_ON_ERROR = False       # True means go until you hit one error
VERBOSE = False

# Files to skip until we reintroduce a manifest reader
skip = ['coverage.json', 'manifest.json', 'representationTests.json']


class TestFile(NamedTuple):
    fullpath: str
    filename: str


def compare_json(j1: str, j2: str, log: TextIO) -> bool:
    """
    Compare two JSON representation
    :param j1: first string
    :param j2: second string
    :param log: log file to record differences
    :return: Result of comparison
    """
    d1 = jao_loads(j1)
    d2 = jao_loads(j2)
    return compare_dicts(d1._as_dict, d2._as_dict, file=log)


def validate_shexj_json(json_str: str, input_fname: str) -> bool:
    """
    Validate json_str against ShEx Schema
    :param json_str: String to validate
    :param input_fname: Name of source file for error reporting
    :return: True if pass
    """
    logger = StringIO()
    shex_obj = jsg_loads(json_str, ShExJ)
    if not is_valid(shex_obj, logger):
        print("File: {} - ".format(input_fname))
        print(logger.getvalue())
        return False
    elif not compare_json(json_str, shex_obj._as_json, logger):
        print("File: {} - ".format(input_fname))
        print(logger.getvalue())
        print(shex_obj._as_json_dumps())
        return False
    return True


def validate_file(file: TestFile) -> bool:
    """
    Download the file in download_url and validate it using the supplied module
    :param file: path and name fo file to download
    :return:
    """
    if file.filename not in skip:
        if VERBOSE:
            print(f"Testing {file.fullpath}")
        if ':' in file.fullpath:
            resp = requests.get(file.fullpath)
            if resp.ok:
                file_text = resp.text
            else:
                print("Error {}: {}".format(resp.status_code, resp.reason))
                return False
        else:
            with open(file.fullpath, 'rb') as f:
                file_text = f.read().decode()
        return validate_shexj_json(file_text, file.fullpath)
    else:
        print("Skipping {}".format(file.fullpath))
        return True


def download_github_file(github_url: str) -> Optional[str]:
    """
    Download the file in github_url
    :param github_url: github url to download
    :return: file contents if success, None otherwise
    """
    print("Downloading {}".format(github_url))
    resp = requests.get(github_url)
    if resp.ok:
        resp = requests.get(resp.json()['download_url'])
        if resp.ok:
            return resp.text
    print("Error {}: {}".format(resp.status_code, resp.reason))
    return None


def validate_shex_schemas() -> bool:
    """
    Validate either the file named in shexTestJson or the files in shexTestRepository against the AST
    :return:
    """
    if not shexTestJson:
        test_list: List[TestFile] = enumerate_http_files(shexTestRepository) if ':' in shexTestRepository else \
            enumerate_directory(shexTestRepository)
        if test_list is None:
            rval = True
        elif STOP_ON_ERROR:
            rval = all(validate_file(e) for e in test_list if e.filename.endswith('.json'))
        else:
            rval = all([validate_file(e) for e in test_list if e.filename.endswith('.json')])
    else:
        return validate_file(TestFile(shexTestJson, shexTestJson.rsplit('/')[1]))
    return rval


def enumerate_http_files(url) -> List[TestFile]:
    resp = requests.get(url)
    if resp.ok:
        for f in resp.json():
            yield TestFile(f['download_url'], f['name'])
    else:
        print("Error {}: {}".format(resp.status_code, resp.reason), file=sys.stderr)


def enumerate_directory(dir_) -> List[TestFile]:
    for fname in os.listdir(dir_):
        fpath = os.path.join(dir_, fname)
        if os.path.isfile(fpath):
            yield TestFile(fpath, fname)


class ShExJValidationTestCase(unittest.TestCase):
    """ Download the contents of the shexTestRepository and make sure that they can all be correctly loaded as
    ShExJSG images.
    """
    @unittest.skipIf(False, "Temporarily disabled - remove me before submit")
    def test_shex_schema(self):
        self.assertTrue(validate_shex_schemas())


if __name__ == '__main__':
    unittest.main()
