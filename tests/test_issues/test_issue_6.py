import unittest
from pyjsg.jsglib.loader import loads as jsg_loads


from ShExJSG import ShExJ


shex = """{
  "@context": [
      "http://www.w3.org/ns/shex.jsonld",
      {
         "@base": "http://bioentity.io/vocab/"
      }
   ],
  "type": "Schema",
  "shapes": [
    {
      "id": "http://a.example/S1",
      "type": "Shape"
    }
  ]
}"""


class ContextTestCase(unittest.TestCase):
    def test_context(self):
        shema = jsg_loads(shex, ShExJ)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
