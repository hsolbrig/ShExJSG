import unittest


from tests import SHEXC_INSTALLED
from ShExJSG.ShExC import ShExC
if SHEXC_INSTALLED:
    from PyShExC.parser_impl.generate_shexj import parse
from rdflib import Graph


shex_c = """
<http://example.org/sample/example1/String> <http://www.w3.org/2001/XMLSchema#string>

<http://example.org/sample/example1/Int> <http://www.w3.org/2001/XMLSchema#integer>

<http://example.org/sample/example1/Boolean> <http://www.w3.org/2001/XMLSchema#boolean>

<http://example.org/sample/example1/Person> EXTRA <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> CLOSED {
    (  <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> [ <http://example.org/model/Person> ]
       ;
       <http://xmlns.com/foaf/0.1/firstName> @<http://example.org/sample/example1/String> * ;
       <http://xmlns.com/foaf/0.1/lastName> @<http://example.org/sample/example1/String> ;
       <http://xmlns.com/foaf/0.1/age> @<http://example.org/sample/example1/Int> ? ;
       <http://example.org/model/living> @<http://example.org/sample/example1/Boolean> ? ;
       <http://example.org/model/living> @<http://example.org/sample/example1/types/Boolean> ? ;
       <http://xmlns.com/foaf/0.1/knows> @<http://example.org/sample/example1/Person> *
    )
}
"""

expected = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ex: <http://example.org/sample/example1/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>


ex:String xsd:string

ex:Int xsd:integer

ex:Boolean xsd:boolean

ex:Person EXTRA rdf:type CLOSED {
    (  rdf:type [ <http://example.org/model/Person> ] ;
       foaf:firstName @ex:String * ;
       foaf:lastName @ex:String ;
       foaf:age @ex:Int ? ;
       <http://example.org/model/living> @ex:Boolean ? ;
       <http://example.org/model/living> @<http://example.org/sample/example1/types/Boolean> ? ;
       foaf:knows @ex:Person *
    )
}"""

expected_base = """BASE <http://example.org/sample/example1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>


<String> xsd:string

<Int> xsd:integer

<Boolean> xsd:boolean

<Person> EXTRA rdf:type CLOSED {
    (  rdf:type [ <http://example.org/model/Person> ] ;
       foaf:firstName @<String> * ;
       foaf:lastName @<String> ;
       foaf:age @<Int> ? ;
       <http://example.org/model/living> @<Boolean> ? ;
       <http://example.org/model/living> @<http://example.org/sample/example1/types/Boolean> ? ;
       foaf:knows @<Person> *
    )
}"""

@unittest.skipIf(not SHEXC_INSTALLED, "Have to install ShExC to run these tests")
class NamespaceTestCase(unittest.TestCase):
    def test_namespaces(self):
        """ Test a graph based namespace manager """
        shex = parse(shex_c)
        g = Graph()
        g.bind('ex', 'http://example.org/sample/example1/')
        g.bind('foaf', 'http://xmlns.com/foaf/0.1/')
        self.assertEqual(expected, str(ShExC(shex, namespaces=g)).strip())

    def test_namespaces2(self):
        """ Test a plain namespace manager """
        shex = parse(shex_c)
        g = Graph()
        g.bind('ex', 'http://example.org/sample/example1/')
        g.bind('foaf', 'http://xmlns.com/foaf/0.1/')
        self.assertEqual(expected, str(ShExC(shex, namespaces=g.namespace_manager)).strip())

    def test_with_base(self):
        """ Test namespaces with base """
        shex = parse(shex_c)
        g = Graph()
        g.bind('ex', 'http://example.org/sample/example1/')
        g.bind('foaf', 'http://xmlns.com/foaf/0.1/')
        self.assertEqual(expected_base,
                         str(ShExC(shex, base='http://example.org/sample/example1/', namespaces=g)).strip())

if __name__ == '__main__':
    unittest.main()
