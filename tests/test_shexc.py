import os
import sys
import unittest
from io import StringIO
from typing import NamedTuple, List, TextIO, Dict

import requests
from dict_compare import compare_dicts
from jsonasobj import loads as jao_loads
from pyjsg.jsglib import loads as jsg_loads
from pyjsg.jsglib.loader import is_valid

from ShExJSG import ShExJ, ShExC
from tests import SHEXC_INSTALLED
if SHEXC_INSTALLED:
    from PyShExC.parser_impl.generate_shexj import parse


# Repository to validate against
shexTestRepository = "https://api.github.com/repos/shexSpec/shexTest/contents/schemas"

# TODO: point this repository back togithub

# shexTestRepository = os.path.abspath(os.path.expanduser("~/git/shexSpec/shexTest/schemas/"))

# If not empty, validate this single file
testShexFile: str = ""

STOP_ON_ERROR = False       # True means go until you hit the first error
VERBOSE = False


NOT_SHEX_FILE = "Not a ShExJ file"
NESTED_AND = "e1 AND (e2 AND e3) vs. e1 AND e2 AND e3"
SEMACT_CHARS = "semAct escapes still need doing"
PATTERN_CHARS = "pattern escapes still need doing"
LITERAL_CHARS = "literal escapes need doing"
USES_IMPORTS = "Imports is a 2.1 feature"
INSANE_BNODE = "Insane BNODE Identifiers"

# Files to skip until we reintroduce a manifest reader
skip = {'coverage.json': NOT_SHEX_FILE,
        'manifest.json': NOT_SHEX_FILE,
        'representationTests.json': NOT_SHEX_FILE
}


if testShexFile and not testShexFile.endswith(".json"):
    testShexFile += ".json"

for k in list(skip.keys()):
    if not k.endswith(".json"):
        skip[k + '.json'] = skip[k]
        del skip[k]


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


def validate_shexc_json(json_str: str, input_fname: str) -> bool:
    """
    Validate json_str against ShEx Schema
    :param json_str: String to validate
    :param input_fname: Name of source file for error reporting
    :return: True if pass
    """
    logger = StringIO()

    # Load the JSON image of the good object and make sure it is valud
    shex_json: ShExJ.Schema = jsg_loads(json_str, ShExJ)
    if not is_valid(shex_json, logger):
        print("File: {} - ".format(input_fname))
        print(logger.getvalue())
        return False

    # Convert the JSON image into ShExC
    shexc_str = str(ShExC(shex_json))

    # Convert the ShExC back into ShExJ
    output_shex_obj = parse(shexc_str)
    if output_shex_obj is None:
        print(f"{input_fname}")
        for number, line in enumerate(shexc_str.split('\n')):
            print(f"{number + 1}: {line}")
        return False
    output_shex_obj["@context"] = "http://www.w3.org/ns/shex.jsonld"
    rval = compare_json(json_str, output_shex_obj._as_json_dumps(), logger)
    if not rval:
        print(shexc_str)
        print(logger.getvalue())
    return rval


class Stats:
    def __init__(self):
        self.total = self.passed = self.skipped = self.failed = 0
        self.skipreasons: Dict[str, int] = {}

    def __str__(self):
        return f"*** Total tests: {self.total}\n" + \
               f"\tPassed: {self.passed}\n" + \
               f"\tSkipped: {self.skipped}\n" + \
               f"\tFailed: {self.failed}\n\n" + \
               "*** Skip Reasons ***\n" + '\n'.join(f"\t{sk} : {self.skipreasons[sk]}"
                                                    for sk in self.skipreasons.keys())


def validate_file(file: TestFile, stats: Stats) -> bool:
    """
    Download the file in download_url and validate it using the supplied module
    :param file: path and name of file to download
    :param stats: Statistics gathering module
    :return:
    """
    stats.total += 1
    if file.filename not in skip:
        if VERBOSE:
            print(f"Testing {file.fullpath}")
        if ':' in file.fullpath:
            resp = requests.get(file.fullpath)
            if resp.ok:
                file_text = resp.text
            else:
                print("Error {}: {}".format(resp.status_code, resp.reason))
                stats.failed += 1
                return False
        else:
            with open(file.fullpath) as f:
                file_text = f.read()
        if validate_shexc_json(file_text, file.fullpath):
            stats.passed += 1
            return True
        else:
            stats.failed += 1
            return False
    else:
        print("Skipping {}".format(file.fullpath))
        stats.skipped += 1
        key = skip[file.filename]
        if key not in stats.skipreasons:
            stats.skipreasons[key] = 0
        stats.skipreasons[key] = stats.skipreasons[key] + 1
        return True


def validate_shex_schemas() -> bool:
    """
    Validate either the file named in shexTestJson or the files in shexTestRepository against the AST
    :return:
    """
    stats = Stats()
    if not testShexFile:
        test_list: List[TestFile] = enumerate_http_files(shexTestRepository) if ':' in shexTestRepository else \
            enumerate_directory(shexTestRepository)
        if test_list is None:
            rval = True
        elif STOP_ON_ERROR:
            rval = all(validate_file(e, stats) for e in test_list if e.filename.endswith('.json'))
        else:
            rval = all([validate_file(e, stats) for e in test_list if e.filename.endswith('.json')])
    else:
        rval = validate_file(TestFile(os.path.join(shexTestRepository, testShexFile), testShexFile), stats)
    print(str(stats))
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


@unittest.skipIf(not SHEXC_INSTALLED, "ShExC must be installed to run this test")
class ShExCValidationTestCase(unittest.TestCase):
    """ 1) Convert the contents of the shexTest/schema's directory into ShExJSG
        2) Convert the ShExJSG into ShExC
        3) Parse the ShExC back into ShExJSG
        4) Compare the input and output JSG's
    """

    def test_shex_schema(self):
        self.assertTrue(validate_shex_schemas())


if __name__ == '__main__':
    unittest.main()
