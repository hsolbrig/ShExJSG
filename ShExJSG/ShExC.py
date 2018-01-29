import re
from typing import List, Any, Optional, Union

from pyjsg.jsglib import jsg
from pyjsg.jsglib.jsg import isinstance_
from pyshexc.parser_impl import generate_shexj

from ShExJSG import ShExJ
from ShExJSG.ShExJ import IRIREF, SemAct


class ShExC:
    def __init__(self, schema: Union[ShExJ.Schema, str]) -> None:
        if isinstance(schema, ShExJ.Schema):
            self.schema = schema
        else:
            self.schema = generate_shexj.parse(schema)

    def __str__(self) -> str:
        schema: List[str] = []
        schema += self.imports(self.schema.imports)
        schema += self.semActs(self.schema.startActs)
        schema += self.shapes(self.schema.shapes)
        rval = ""
        rline = ""
        for e in schema:
            if len(rline + e) > 60:
                rval += rline + '\n'
                rline = ""
            rline += " " + e
        rval += rline + '\n'
        return rval

    def __repr__(self) -> str:
        rval: List[str] = []
        rval += self.imports(self.schema.imports)
        rval += self.semActs(self.schema.startActs)
        rval += self.shapes(self.schema.shapes)
        return ' '.join(e for e in rval if e)

    def implementation_error(self, tkn: Any) -> None:
        raise NotImplementedError(f"Unknown token: {type(tkn)}")

    def imports(self, imports: Optional[List[IRIREF]]) -> List[str]:
        if imports is not None:
            return [f"IMPORT {self.iriref(e)}" for e in imports]
        return []

    def semActs(self, semActs: Optional[List[SemAct]]) -> List[str]:
        rval = []
        if semActs is not None:
            for act in semActs:
                rval.append(f"%{self.iriref(act.name)}")
                rval.append(f"{{{act.code}%}}" if act.code.val is not None else '%')
        return rval

    def shapes(self, shapes: Optional[List[ShExJ.shapeExpr]]) -> List[str]:
        rval = []
        if shapes is not None:
            for sexpr in shapes:
                rval += self.shapeExpr(sexpr)
        return rval

    def shapeExpr(self, sexpr: ShExJ.shapeExpr) -> List[str]:
        if isinstance(sexpr, ShExJ.ShapeOr):
            return self.shapeOr(sexpr)
        elif isinstance(sexpr, ShExJ.ShapeAnd):
            return self.shapeAnd(sexpr)
        elif isinstance(sexpr, ShExJ.ShapeNot):
            return self.shapeNot(sexpr)
        elif isinstance(sexpr, ShExJ.NodeConstraint):
            return self.nodeConstraint(sexpr)
        elif isinstance(sexpr, ShExJ.Shape):
            return self.shape(sexpr)
        elif isinstance_(sexpr, ShExJ.shapeExprLabel):
            return [self.shapeExprRef(sexpr)]
        elif isinstance(sexpr, ShExJ.ShapeExternal):
            return [self.shapeExternal(sexpr)]
        else:
            self.implementation_error(sexpr)

    def shapeOr(self, shapeOr: ShExJ.ShapeOr) -> List[str]:
        rval = [self.shapeExprLabel(shapeOr.id)] + self.shapeExpr(shapeOr.shapeExprs[0]) + ['OR']
        for e in shapeOr.shapeExprs[1:-1]:
            rval += self.shapeExpr(e) + ['OR']
        rval += self.shapeExpr(shapeOr.shapeExprs[-1])
        return rval

    def shapeAnd(self, shapeAnd: ShExJ.ShapeAnd) -> List[str]:
        rval = [self.shapeExprLabel(shapeAnd.id)] + self.shapeExpr(shapeAnd.shapeExprs[0]) + ['AND']
        for e in shapeAnd.shapeExprs[1:-1]:
            rval += self.shapeExpr(e) + ['AND']
        rval += self.shapeExpr(shapeAnd.shapeExprs[-1])
        return rval

    def shapeNot(self, shapeNot: ShExJ.ShapeNot) -> List[str]:
        return [self.shapeExprLabel(shapeNot.id)] + ['NOT ('] + self.shapeExpr(shapeNot.shapeExpr) + [')']

    def nodeConstraint(self, nc: ShExJ.NodeConstraint) -> List[str]:
        rval = [self.shapeExprLabel(nc.id)]
        if nc.nodeKind:
            rval += [str(nc.nodeKind).upper()]
        if nc.datatype:
            rval += [self.iriref(nc.datatype)]
        rval += self.xsFacet(nc)
        if nc.values is not None:
            rval.append('[')
            for e in nc.values:
                rval += self.valueSetValue(e)
            rval.append(']')
        return rval

    def shape(self, shape: ShExJ.Shape) -> List[str]:
        rval = [self.shapeExprLabel(shape.id)]
        if shape.extra is not None:
            rval += ['EXTRA'] + [self.iriref(e) for e in shape.extra]
        if shape.closed.val:
            rval += ['CLOSED']
        rval += ['{'] + self.tripleExpr(shape.expression) + ['}']
        if shape.annotations:
            rval += self.annotations(shape.annotations)
        if shape.semActs:
            rval += self.semActs(shape.semActs)
        return rval

    def shapeExternal(self, se: ShExJ.ShapeExternal) -> str:
        return self.shapeExprLabel(se.id) + '{ }'

    def tripleExpr(self, te: ShExJ.tripleExpr) -> List[str]:
        if te is None:
            return []
        elif isinstance(te, ShExJ.EachOf):
            return self.eachOf(te)
        elif isinstance(te, ShExJ.OneOf):
            return self.oneOf(te)
        elif isinstance(te, ShExJ.TripleConstraint):
            return self.tripleConstraint(te)
        elif isinstance_(te, ShExJ.tripleExprLabel):
            return ['&' + self.tripleExprLabel(te)]
        else:
            self.implementation_error(te)

    def eachOf(self, eo: ShExJ.EachOf) -> List[str]:
        return self._eachOneOf(eo, ';')

    def oneOf(self, oo: ShExJ.OneOf) -> List[str]:
        return self._eachOneOf(oo, '|')

    def _eachOneOf(self, eoo: Union[ShExJ.EachOf, ShExJ.OneOf], sep: str) -> List[str]:
        rval = ['$' + self.tripleExprLabel(eoo.id)] if eoo.id is not None else []
        rval += ['(']
        rval += self.tripleExpr(eoo.expressions[0])
        for expr in eoo.expressions[1:]:
            rval += [sep] + self.tripleExpr(expr)
        rval += [')' + self.cardinality(eoo.min, eoo.max)]
        rval += self.semActs(eoo.semActs)
        rval += self.annotations(eoo.annotations)
        return rval

    def tripleConstraint(self, tc: ShExJ.TripleConstraint) -> List[str]:
        rval = ['$' + self.tripleExprLabel(tc.id)] if tc.id else []
        rval += [('^' if tc.inverse.val else '') + self.iriref(tc.predicate)] + \
            (self.shapeExpr(tc.valueExpr) if tc.valueExpr is not None else ['.'])
        rval += self.cardinality(tc.min, tc.max)
        rval += self.semActs(tc.semActs)
        rval += self.annotations(tc.annotations)
        return rval

    def annotations(self, annotations: Optional[List[ShExJ.Annotation]]) -> List[str]:
        if annotations:
            return ['// ' + self.iriref(annot.predicate) + self.objectValue(annot.object) for annot in annotations]
        else:
            return []

    @staticmethod
    def cardinality(min_: Optional[jsg.Integer], max_: Optional[jsg.Integer]) -> str:
        minv = 1 if min_.val is None else min_.val
        maxv = 1 if max_.val is None else max_.val
        if minv == 0:
            if maxv == 1:
                return '?'
            elif maxv == -1:
                return '*'
        elif minv == 1:
            if maxv == -1:
                return '+'
            elif maxv == 1:
                return ""
        return f"{{{minv}}}" if minv == maxv else f"{{{minv},{maxv}}}" if maxv != -1 else f"{{{minv},*}}"

    @staticmethod
    def add_facet(facet, label: str) -> str:
        return f'{label} {facet}' if facet.val is not None else ''

    @staticmethod
    def add_pattern(pattern, flags) -> str:
        if pattern.val:
            pval = re.sub(r'/', r'\/', pattern.val)
            return f'/{pval}/' + (flags.val if flags.val is not None else '')
        return ''

    def xsFacet(self, nc: ShExJ.NodeConstraint) -> List[str]:
        return [self.add_facet(nc.length, 'LENGTH'),
                self.add_facet(nc.minlength, 'MINLENGTH'),
                self.add_facet(nc.maxlength, 'MAXLENGTH'),
                self.add_pattern(nc.pattern, nc.flags),
                self.add_facet(nc.mininclusive, 'MININCLUSIVE'),
                self.add_facet(nc.minexclusive, 'MINEXCLUSIVE'),
                self.add_facet(nc.maxinclusive, 'MAXINCLUSIVE'),
                self.add_facet(nc.maxexclusive, 'MAXEXCLUSIVE'),
                self.add_facet(nc.totaldigits, 'TOTALDIGITS'),
                self.add_facet(nc.fractiondigits, 'FRACTIONDIGITS')]

    def valueSetValue(self, vsv: ShExJ.valueSetValue) -> List[str]:
        if isinstance_(vsv, ShExJ.objectValue):
            return [self.objectValue(vsv)]
        elif isinstance(vsv, ShExJ.IriStem):
            return [self.iriStem(vsv)]
        elif isinstance(vsv, ShExJ.IriStemRange):
            return self.iriStemRange(vsv)
        elif isinstance(vsv, ShExJ.LiteralStem):
            return [self.literalStem(vsv)]
        elif isinstance(vsv, ShExJ.LiteralStemRange):
            return self.literalStemRange(vsv)
        elif isinstance(vsv, ShExJ.Language):
            return [self.language(vsv.languageTag)]
        elif isinstance(vsv, ShExJ.LanguageStem):
            return [self.languageStem(vsv)]
        elif isinstance(vsv, ShExJ.LanguageStemRange):
            return self.languageStemRange(vsv)
        else:
            self.implementation_error(vsv)

    def objectValue(self, v: ShExJ.objectValue) -> str:
        if isinstance(v, ShExJ.IRIREF):
            return self.iriref(v)
        elif isinstance(v, ShExJ.ObjectLiteral):
            return self.objectLiteral(v)
        else:
            self.implementation_error(v)

    def objectLiteral(self, v: ShExJ.ObjectLiteral) -> str:
        return f'"{v.value}"' + (f"@{v.language}" if v.language else f"^^{self.iriref(v.type)}" if v.type else "")

    def iriStem(self, v: ShExJ.IriStem) -> str:
        return self.iriref(v.stem) + '~'

    def iriStemRange(self, v: ShExJ.IriStemRange) -> [str]:
        return [('.' if isinstance(v.stem, ShExJ.Wildcard) else self.iriStem(v))] + \
               [f" - {self.iriref(e) if isinstance(e, ShExJ.IRIREF) else self.iriStem(e)}" for e in v.exclusions]

    def literalStem(self, v: ShExJ.LiteralStem) -> str:
        return self.literal(v.stem) + '~'

    @staticmethod
    def literal(v) -> str:
        return f'"{v}"'

    def literalStemRange(self, v: ShExJ.LiteralStemRange) -> [str]:
        return [('.' if isinstance(v.stem, ShExJ.Wildcard) else self.literalStem(v))] + \
               [f' - {self.literal(e) if isinstance(e, jsg.JSGString) else self.literalStem(e)}' for e in v.exclusions]

    @staticmethod
    def language(v: ShExJ.LANGTAG) -> str:
        return '@' + str(v)

    def languageStem(self, v: ShExJ.LanguageStem) -> str:
        return self.language(v.stem) + '~'

    def languageStemRange(self, v: ShExJ.LanguageStemRange) -> [str]:
        return [('.' if isinstance(v.stem, ShExJ.Wildcard) else self.languageStem(v))] + \
               [f" - {self.language(e) if isinstance(e, ShExJ.LANGTAG) else self.languageStem(e)}"
                for e in v.exclusions]

    def shapeExprLabel(self, shapeExprLabel: ShExJ.shapeExprLabel) -> str:
        return self.exprLabel(shapeExprLabel)

    def shapeExprRef(self, shapeExprRef: ShExJ.shapeExprLabel) -> str:
        # TODO: this is an issue in the JSG - the type should be shapeExprRef
        return '@' + self.exprLabel(shapeExprRef)

    def tripleExprLabel(self, tripleExprLabel: ShExJ.tripleExprLabel) -> str:
        return self.exprLabel(tripleExprLabel)

    def exprLabel(self, label: Union[ShExJ.shapeExprLabel, ShExJ.tripleExprLabel]) -> str:
        if label is None:
            return ""
        elif isinstance(label, IRIREF):
            return self.iriref(label)
        elif isinstance(label, ShExJ.BNODE):
            return self.bnode(label)
        else:
            self.implementation_error(label)

    @staticmethod
    def bnode(v: ShExJ.BNODE) -> str:
        return str(v)

    @staticmethod
    def iriref(v: ShExJ.IRIREF) -> str:
        return f"<{v}>"
