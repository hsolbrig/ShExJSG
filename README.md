# Python representation of the ShEx AST(ish) specification

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

