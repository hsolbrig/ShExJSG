import os
import sys
import unittest
from typing import NamedTuple, List

import requests
from dict_compare import compare_dicts
from jsonasobj import loads as jao_loads
from pyjsg.jsglib.jsg import loads as jsg_loads
from pyjsg.jsglib.logger import Logger
from pyshexc.parser_impl import generate_shexj

from ShExJSG import ShExJ, ShExC
from tests.utils.memlogger import MemLogger

# Repository to validate against
# shexTestRepository = "https://api.github.com/repos/shexSpec/shexTest/contents/schemas?ref=2.0"

shexTestRepository = os.path.abspath(os.path.expanduser("~/Development/git/shexSpec/shexTest/schemas/"))

# If not empty, validate this single file
testShexFile: str = ""
# testShexFile = "https://raw.githubusercontent.com/shexSpec/shexTest/2.0/schemas/" \
#                "1dotRefAND3.json"


STOP_ON_ERROR = False       # True means go until you hit the first error


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
        '1dotANDopen1dotAND1dotclose.json': NESTED_AND,
        '1dotCodeWithEscapes1.json': SEMACT_CHARS,
        '1dotIMPORT1dot.json': USES_IMPORTS,
        "1literalPattern_with_all_meta.json": PATTERN_CHARS,
        "1literalPattern_with_REGEXP_escapes.json": PATTERN_CHARS,
        "1literalPattern_with_REGEXP_escapes_bare.json": PATTERN_CHARS,
        "1refbnode_with_spanning_PN_CHARS1.json": INSANE_BNODE,
        "1refbnode_with_spanning_PN_CHARS_BASE1.json": INSANE_BNODE,
        "1val1STRING_LITERAL1_with_all_punctuation.json": LITERAL_CHARS,
        "1val1STRING_LITERAL1_with_ECHAR_escapes": LITERAL_CHARS,
        "1val1STRING_LITERAL1_with_NO_ECHAR_escapes": LITERAL_CHARS,
        "1valExprRef-IV1": USES_IMPORTS,
        "1valExprRefbnode-IV1": USES_IMPORTS,
        "2EachInclude1-IS2": USES_IMPORTS,
        "2RefS1-Icirc": USES_IMPORTS,
        "2RefS1-IS2": USES_IMPORTS,
        "2RefS2-Icirc": USES_IMPORTS,
        "2RefS2-IS1": USES_IMPORTS,
        "3circRefS1-Icirc": USES_IMPORTS,
        "3circRefS1-IS2-IS3-IS3": USES_IMPORTS,
        "3circRefS1-IS2-IS3": USES_IMPORTS,
        "3circRefS1-IS23": USES_IMPORTS,
        "3circRefS123-Icirc": USES_IMPORTS,
        "3circRefS2-Icirc": USES_IMPORTS,
        "3circRefS2-IS3": USES_IMPORTS,
        "3circRefS3-IS12": USES_IMPORTS,
        "3circRefS3-Icirc": USES_IMPORTS,
        "_all": "Just insane",
        "kitchenSink": "Just insane",
        "NOT1dotOR2dotX3": "Nesting issue",
        "NOT1dotOR2dotX3AND1": "Nesting issue"}


if testShexFile and not testShexFile.endswith(".json"):
    testShexFile += ".json"

for k in list(skip.keys()):
    if not k.endswith(".json"):
        skip[k + '.json'] = skip[k]
        del skip[k]


class TestFile(NamedTuple):
    fullpath: str
    filename: str


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


def validate_shexc_json(json_str: str, input_fname: str) -> bool:
    """
    Validate json_str against ShEx Schema
    :param json_str: String to validate
    :param input_fname: Name of source file for error reporting
    :return: True if pass
    """
    logger = Logger(MemLogger('\t'))

    # Load the JSON image of the good object and make sure it is valud
    shex_json: ShExJ.Schema = jsg_loads(json_str, ShExJ)
    if not shex_json._is_valid(logger):
        print("File: {} - ".format(input_fname))
        print(logger.text)
        return False

    # Convert the JSON image into ShExC
    shexc_str = str(ShExC(shex_json))

    # Convert the ShExC back into ShExJ
    output_shex_obj = ShExC(shexc_str).schema
    if output_shex_obj is None:
        return False
    output_shex_obj["@context"] = "http://www.w3.org/ns/shex.jsonld"
    rval = compare_json(json_str, output_shex_obj._as_json_dumps(), logger)
    if not rval:
        print(shexc_str)
        print(logger.text)
    return rval



class Stats:
    def __init__(self):
        self.total = self.passed = self.skipped = self.failed = 0

    def __str__(self):
        return f"*** Total tests: {self.total}\n" + \
               f"\tPassed: {self.passed}\n" + \
               f"\tSkipped: {self.skipped}\n" + \
               f"\tFailed: {self.failed}"


def validate_file(file: TestFile, stats: Stats) -> bool:
    """
    Download the file in download_url and validate it using the supplied module
    :param file: path and name of file to download
    :return:
    """
    stats.total += 1
    if file.filename not in skip:
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
