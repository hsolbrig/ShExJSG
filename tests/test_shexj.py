import unittest
from typing import Optional

import requests
from dict_compare import compare_dicts
from jsonasobj import loads as jao_loads

from pyjsg.jsglib.logger import Logger
from pyjsg.jsglib.jsg import loads as jsg_loads

from ShExJSG import ShExJ
from tests.utils.memlogger import MemLogger


# Repository to validate against
shexTestRepository = "https://api.github.com/repos/shexSpec/shexTest/contents/schemas?ref=2.0"

# If not empty, validate this single file
shexTestJson: str = None
# shexTestJson = "https://raw.githubusercontent.com/shexSpec/shexTest/2.0/schemas/" \
#                "1refbnode_with_spanning_PN_CHARS_BASE1.json"


STOP_ON_ERROR = False       # True means go until you hit one error

# Files to skip until we reintroduce a manifest reader
skip = ['coverage.json', 'manifest.json']


def compare_json(j1: str, j2: str, log: Logger) -> bool:
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
    logger = Logger(MemLogger('\t'))
    shex_obj = jsg_loads(json_str, ShExJ)
    if not shex_obj._is_valid(logger):
        print("File: {} - ".format(input_fname))
        print(logger.text)
        return False
    elif not compare_json(json_str, shex_obj._as_json, logger):
        print("File: {} - ".format(input_fname))
        print(logger.text)
        print(shex_obj._as_json_dumps())
        return False
    return True


def validate_file(download_url: str) -> bool:
    """
    Download the file in download_url and validate it using the supplied module
    :param download_url: url of file to download
    :return:
    """
    fname = download_url.rsplit('/', 1)[1]
    if fname not in skip:
        print("Testing {}".format(download_url))
        resp = requests.get(download_url)
        if resp.ok:
            return validate_shexj_json(resp.text, download_url)
        else:
            print("Error {}: {}".format(resp.status_code, resp.reason))
            return False
    print("Skipping {}".format(download_url))
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
        resp = requests.get(shexTestRepository)
        if resp.ok:
            if STOP_ON_ERROR:
                return all(validate_file(f['download_url']) for f in resp.json() if f['name'].endswith('.json'))
            else:
                return all([validate_file(f['download_url']) for f in resp.json() if f['name'].endswith('.json')])
        else:
            print("Error {}: {}".format(resp.status_code, resp.reason))
    else:
        return validate_file(shexTestJson)
    return False


class ShExJValidationTestCase(unittest.TestCase):
    """ Download the contents of the shexTestRepository and make sure that they can all be correctly loaded as
    ShExJSG images.
    """

    def test_shex_schema(self):
        self.assertTrue(validate_shex_schemas())


if __name__ == '__main__':
    unittest.main()
