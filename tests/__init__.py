# Settings for rdflib parsing issue

#         See line 1578 in notation3.py:
#                 k = 'abfrtvn\\"\''.find(ch)
#                 if k >= 0:
#                     uch = '\a\b\f\r\t\v\n\\"\''[k]
import os

RDFLIB_PARSING_ISSUE_FIXED = False

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
input_data_dir = os.path.join(data_dir, 'input')
output_data_dir = os.path.join(data_dir, 'output')

import sys

SHEXC_INSTALLED = True
try:
    import pyshexc
except ModuleNotFoundError:
    SHEXC_INSTALLED = False
SHEXC_INSTALLED = 'pyshexc' in sys.modules

if SHEXC_INSTALLED:
    print("Tests will include pyshexc module")



# Repository to validate against
shexTestRepository_github = "https://api.github.com/repos/shexSpec/shexTest/contents/schemas"

shexTestRepository = shexTestRepository_github
# THIS only works on local tests.  Make sure it is removed before commit
shexTestRepository = os.path.abspath(os.path.expanduser("~/git/shexSpec/shexTest/schemas/"))
if shexTestRepository != shexTestRepository_github:
    from warnings import warn
    warn(f"Shex test repository is pointed at a local image: {shexTestRepository}")
