from ctypeslib.codegen.gccxmlparser import parse
from ctypeslib.codegen import typedesc

class Func:
    def __init__(self, func):
        self.name = func.name
        self.returns = self._parse_type_arg(func.returns)
        self.args = [self._parse_type_arg(arg) for arg in func.iterArgTypes()]

    def signature(self):
        return "%s %s(%s)" % (self.returns, self.name, ", ".join(self.args))

    def _parse_type_arg(self, tp):
        if isinstance(tp, typedesc.FundamentalType):
            return tp.name
        elif isinstance(tp, typedesc.PointerType):
            return parse_type(tp.typ) + '*'
        elif isinstance(tp, typedesc.CvQualifiedType):
            return parse_type(tp.typ)
        elif isinstance(tp, typedesc.Typedef):
            return tp.name
        elif isinstance(tp, typedesc.Structure):
            return tp.name
        else:
            raise ValueError("yoyo", type(tp))

def parse_type(tp):
    if isinstance(tp, typedesc.FundamentalType):
        return tp.name
    elif isinstance(tp, typedesc.PointerType):
        if isinstance(tp.typ, typedesc.FunctionType):
            args = [parse_type_arg(arg) for arg in tp.typ.iterArgTypes()]
            return parse_type(tp.typ.returns) + '(*%s)' + '(%s)' % ", ".join(args)
        else:
            return parse_type(tp.typ) + '*'
    elif isinstance(tp, typedesc.CvQualifiedType):
        #return 'const ' + parse_type(tp.typ)
        return parse_type(tp.typ)
    elif isinstance(tp, typedesc.Typedef):
        return tp.name
    elif isinstance(tp, typedesc.Structure):
        return tp.name
    elif isinstance(tp, typedesc.FunctionType):
        return ""
    else:
        raise ValueError("yoyo", type(tp))
