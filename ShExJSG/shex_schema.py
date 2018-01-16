from ShExJSG import ShExJ


def Schema() -> ShExJ.Schema:
    """ Constructor for a ShEx schema """
    schema = ShExJ.Schema()
    schema['@context'] = "http://www.w3.org/ns/shex.jsonld"
    return schema
