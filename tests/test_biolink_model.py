import os
import unittest

from ShExJSG import ShExC, ShExJ
from tests import input_data_dir, output_data_dir
from pyjsg.jsglib.loader import load

update_output = False


class BioLinkShexCTestCase(unittest.TestCase):
    def do_test(self, infile: str) -> None:
        outfile = os.path.join(output_data_dir, infile.rsplit('.', 1)[0] + '.shex')
        shexj = load(os.path.join(input_data_dir, infile), ShExJ)
        shexc = ShExC(shexj)
        self.assertIsNotNone(shexc)
        shexc_text = str(shexc)
        if update_output:
            with open(outfile, 'w') as outf:
                outf.write(shexc_text)
        with open(outfile) as outf:
            target_shexc = outf.read()
        self.maxDiff = None
        self.assertEqual(target_shexc, shexc_text)
        self.assertFalse(update_output, "update_output is set to True")

    def test_conversion(self):
        """ Test the ShExC emitter using the biolink model """
        self.maxDiff = None
        self.do_test('biolink-model.json')

    def test_shortand(self):
        self.do_test('shortand.json')

    def test_list(self):
        self.do_test('list.json')

    def test_meta(self):
        self.do_test('meta.json')


if __name__ == '__main__':
    unittest.main()
