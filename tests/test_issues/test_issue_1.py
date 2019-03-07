import unittest

from pyjsg.jsglib.loader import is_valid


class ContextTestCase(unittest.TestCase):
    def test_default_context(self):
        from ShExJSG import Schema

        schema = Schema()
        schema.start = "blabla"
        self.assertTrue(is_valid(schema))


if __name__ == '__main__':
    unittest.main()
