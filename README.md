# ShExJSG - 
Python representation of the ShEx AST(ish) specification. 

## History
* 0.2.0 - alpha release of ShExC emitter
* 0.2.1 - add 'start' to emitter_
* 0.3.0 - Updated to PyJSG 0.8b1
* 0.5.0 - first candidate for ShEx 2.1
* 0.5.1 - beta ShEx 2.1

[![Pyversions](https://img.shields.io/pypi/pyversions/ShExJSG.svg)](https://pypi.python.org/pypi/ShExJSG)

[![PyPi](https://img.shields.io/pypi/v/ShExJSG.svg)](https://pypi.python.org/pypi/ShExJSG)


## Use:
```python
from ShExJSG import Schema, ShExJ
from PyShExC import ShExC

schema = Schema()

schema.start = ShExJ.Shape()

print(schema._is_valid())
print(schema._as_json_dumps())
print(str(ShExC(schema)))
```
```text
True
{
   "@context": "http://www.w3.org/ns/shex.jsonld",
   "start": {
      "type": "Shape"
   },
   "type": "Schema"
}
 start=  { }
```




## ShExJ.jsg
This file is derived from the [ShEx JSG specification](https://github.com/shexSpec/shexTest/blob/master/doc/ShExJ.jsg).  The differences are as follows:

1) **`labeledShapeExpr`** - The official JSG implemention specifies a strange pattern where the objects with a `type` of `"ShapeOr"`, `"ShapeAnd"`, ... are recognized as instances of `ShapeOr`, `ShapeAnd`, ... if they lack an `id` element and as `labeledShapeOr`, `labeledShapeAnd`, ... if the `id` element exists.  We simplify this construct, leaving `id` optional.  This potentially allows the parser to accept some highly unlikely invalid constructs, but these can be checked in a post-parse step if you feel deeply about it. (Note also that the [ShEx semantics](http://shex.io/shex-semantics/#node-constraints) document does not include the **`labeledShapeExpr`** branch)
2) This uses the [revised jsg](https://github.com/hsolbrig/pyjsg) syntax.


## ShExJ.py
Output of the [PyJSG](https://github.com/hsolbrig/pyjsg) `generate_parser` for ShExJ.jsg.  Python 3 representation of the ShEx AST


## Installation

This package currently requires python 3.6 or later.  It could be updated to support earlier python 3 versions if there is sufficient demand.

```text
pip install ShExJSG
```

## Updating the parser
```bash
cd ShExJSG
generate_parser ShExJ.jsg
```

Then run all of the unit tests