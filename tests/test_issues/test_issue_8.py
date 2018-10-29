import unittest

from pyjsg.jsglib import loads as jsg_loads

from ShExJSG import ShExC, ShExJ

shexj = """{
   "type": "Schema",
   "@context": [
      "http://www.w3.org/ns/shex.jsonld",
      {
         "@base": "http://bioentity.io/vocab/"
      }
   ],
   "shapes": [
       {
         "type": "ShapeAnd",
         "id": "http://bioentity.io/vocab/BiologicalEntity",
         "shapeExprs": [
            "http://bioentity.io/vocab/NamedThing",
            {
               "type": "Shape",
               "expression": {
                  "type": "TripleConstraint",
                  "predicate": "http://purl.obolibrary.org/obo/RO_0002200",
                  "valueExpr": {
                     "type": "NodeConstraint"
                  },
                  "min": 0,
                  "max": 1
               }
            }
         ]
       }
    ]
}
"""


class EmptyNodeConstraintTestCase(unittest.TestCase):
    def test_empty(self):
        shex_json: ShExJ.Schema = jsg_loads(shexj, ShExJ)
        shexc_str = str(ShExC(shex_json))
        shex_c = ShExC(shexc_str)
        self.assertIsNotNone(shex_c.schema)


if __name__ == '__main__':
    unittest.main()
