from ctypeslib.codegen import typedesc

from cytypes import generic_decl

def typedef_as_arg(tp):
    return tp.name

def fundamental_as_arg(tp):
    return tp.name

def structure_as_arg(tp):
    return tp.name

def union_as_arg(tp):
    return tp.name

def pointer_as_arg(tp):
    if isinstance(tp.typ, typedesc.FunctionType):
        args = [generic_as_arg(arg) for arg in tp.typ.iterArgTypes()]
        if len(args) > 0:
            return generic_as_arg(tp.typ.returns) + \
                   ' (*)(%s)' % ", ".join(args)
        else:
            return generic_as_arg(tp.typ.returns) + ' (*)()'
    else:
        return '%s *' % generic_as_arg(tp.typ)

def generic_as_arg(tp):
    if isinstance(tp, typedesc.FundamentalType):
        return fundamental_as_arg(tp)
    elif isinstance(tp, typedesc.Typedef):
        return typedef_as_arg(tp)
    elif isinstance(tp, typedesc.PointerType):
        return pointer_as_arg(tp)
    elif isinstance(tp, typedesc.CvQualifiedType):
        return generic_as_arg(tp.typ)
    elif isinstance(tp, typedesc.Structure):
        return structure_as_arg(tp)
    elif isinstance(tp, typedesc.Union):
        return union_as_arg(tp)
    elif isinstance(tp, typedesc.Enumeration):
        return "int"
    else:
        print "Argument not handled in generic_as_arg", tp
        return None

def find_unqualified_type(tp):
    if isinstance(tp, typedesc.FundamentalType) or \
       isinstance(tp, typedesc.Structure) or \
       isinstance(tp, typedesc.Union) or \
       isinstance(tp, typedesc.Enumeration) or \
       isinstance(tp, typedesc.Typedef):
        return tp
    elif isinstance(tp, typedesc.CvQualifiedType) or \
         isinstance(tp, typedesc.PointerType):
        return find_unqualified_type(tp.typ)
    elif isinstance(tp, typedesc.FunctionType):
        return None
    else:
        raise ValueError("Unhandled type %s" % str(tp))

def named_pointer_decl(tp):
    if isinstance(tp.typ, typedesc.FunctionType):
        args = [generic_decl(arg) for arg in tp.typ.iterArgTypes()]
        return generic_decl(tp.typ.returns) + '(*%s)' + '(%s)' % ", ".join(args)
    else:
        return generic_decl(tp.typ) + ' * %s'

