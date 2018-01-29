import re
from typing import Optional, List, Dict, Union, Any

from pyjsg.jsglib import jsg
from pyjsg.jsglib.jsg import isinstance_

from ShExJSG import ShExJ
from ShExJSG.ShExJ import IRIREF, SemAct, shapeExpr


class Schema(ShExJ.Schema):
    """ Wrapper for ShExJ Schema with the JSON-LD context element """
    def __init__(self,
                 imports: Optional[List[IRIREF]] = None,
                 startActs: Optional[List[SemAct]] = None,
                 start: Optional[shapeExpr] = None,
                 shapes: Optional[List[shapeExpr]] = None,
                 **_kwargs: Dict[str, object]):
        super().__init__(imports, startActs, start, shapes, **_kwargs)
        self['@context'] = "http://www.w3.org/ns/shex.jsonld"
