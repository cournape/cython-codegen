from ctypeslib.codegen import typedesc

def typedef_decl(tp):
    if not isinstance(tp.typ, typedesc.PointerType):
        return "typedef %s %s" % (tp.typ.name, tp.name)
    else:
        return "typedef %s" % (pointer_decl(tp.typ) % tp.name)

# Is declaration/definition the same for typedefs ?
typedef_def = typedef_decl

def pointer_decl(tp):
    if isinstance(tp.typ, typedesc.FunctionType):
        args = [generic_decl(arg) for arg in tp.typ.iterArgTypes()]
        return generic_decl(tp.typ.returns) + '(*%s)' + '(%s)' % ", ".join(args)
    else:
        return '%s *'

def struct_decl(tp):
    return "struct %s" % tp.name

def struct_def(tp, indent=None):
    output = ['struct %s:' % tp.name]
    for f in tp.members:
        if isinstance(f, typedesc.Field):
            output.append("    %s %s" % (generic_decl(f.typ), f.name))
        elif isinstance(f, typedesc.Structure):
            output.append("    %s" % generic_decl(f))
        else:
            print "Struct member not handled:", f
    if not tp.members:
        output.append("    pass")

    if indent:
        return "\n".join([indent + i for i in output])
    else:
        return "\n".join(output)

def generic_decl(tp):
    if isinstance(tp, typedesc.Typedef):
        return typedef_decl(tp)
    elif isinstance(tp, typedesc.Structure):
        return struct_decl(tp)
    elif isinstance(tp, typedesc.FundamentalType):
        return tp.name
    else:
        print "Not handled: ", tp

def generic_def(tp):
    if isinstance(tp, typedesc.Typedef):
        return typedef_def(tp)
    elif isinstance(tp, typedesc.Structure):
        return struct_def(tp)
    else:
        print "Not handled: ", tp

