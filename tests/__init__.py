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

SHEXC_INSTALLED = 'pyshexc' in sys.modules
if SHEXC_INSTALLED:
    print("Tests will include pyshexc module")
