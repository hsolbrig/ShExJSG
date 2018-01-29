import unittest

import os

from pyjsg.jsglib.jsg import loads

from ShExJSG import ShExC, ShExJ


class GraphShExTestCase(unittest.TestCase):
    def test_graph_shexc(self):
        json_file = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'data', 'graph_shex.json')
        with open(json_file) as f:
            graph_schema: ShExJ.Schema = loads(f.read(), ShExJ)
        print(str(ShExC(graph_schema)))
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
