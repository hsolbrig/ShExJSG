import unittest


class ContextTestCase(unittest.TestCase):
    def test_default_context(self):
        from ShExJSG import Schema

        schema = Schema()
        schema.start = "blabla"
        self.assertTrue(schema._is_valid())


if __name__ == '__main__':
    unittest.main()
