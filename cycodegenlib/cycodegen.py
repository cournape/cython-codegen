import sys
import re

from ctypeslib.codegen import typedesc
from tp_puller import TypePuller
from misc import classify, query_items
from cytypes import generic_decl, generic_named_decl
from funcs import generic_as_arg, named_pointer_decl

def generate_cython(output, genitems, enumvals):
    # Generate the cython code
    cython_code = [cy_generate(i) for i in genitems]

    if enumvals:
        output.write("\tcdef enum:\n")
        for i in enumvals:
            output.write("\t\t%s = %d\n" % (i.name, int(i.value)))
    for i in cython_code:
        if not i:
            continue
        if len(i) > 1:
            output.write("\t%s\n" % i[0])
            for j in i[1:]:
                output.write("\t%s\n" % j)
        else:
            output.write("\t%s\n" % i[0])

def cy_generate_typedef(item):
    if not isinstance(item.typ, typedesc.PointerType):
        return ["ctypedef %s %s" % (item.typ.name, item.name)]
    else:
        return ["ctypedef %s" % (named_pointer_decl(item.typ) % item.name)]

def cy_generate_structure(tp, union=False):
    if union:
        output = ['cdef union %s:' % tp.name]
    else:
        output = ['cdef struct %s:' % tp.name]
    for m in tp.members:
        if isinstance(m, typedesc.Field):
            output.append("\t" + (generic_named_decl(m.typ) % m.name))
        elif isinstance(m, typedesc.Structure):
            output.append("\t%s" % generic_decl(m))
        else:
            print "Struct member not handled:", m
    if not tp.members:
        output.append("\tpass")

    return output

def cy_generate_enumeration(tp):
    output = ['cdef enum %s:' % tp.name]
    for v in tp.values:
        output.append("\t%s = %s" % (v.name, v.value))

    return output

def cy_generate_function(func):
    args = [generic_as_arg(a) for a in func.iterArgTypes()]
    return ["%s %s(%s)" % (generic_as_arg(func.returns), 
            func.name, ", ".join(args))]

def cy_generate_enum_value(tp):
    output = ['cdef enum:']
    output.append("\t%s = %d" % (tp.name, int(tp.value)))
    return output

def cy_generate(item):
    if isinstance(item, typedesc.Typedef):
        #print "Typedef Generating", item, item.name
        return cy_generate_typedef(item)
    elif isinstance(item, typedesc.Structure):
        #print "Struct Generating", item, item.name
        return cy_generate_structure(item)
    elif isinstance(item, typedesc.Union):
        #print "Union Generating", item, item.name
        return cy_generate_structure(item, union=True)
    elif isinstance(item, typedesc.Function):
        #print "FunctionType Generating", item, item.name
        return cy_generate_function(item)
    elif isinstance(item, typedesc.EnumValue):
        #print "FunctionType Generating", item
        return cy_generate_enum_value(item)
    elif isinstance(item, typedesc.Enumeration):
        #print "FunctionType Generating", item
        return cy_generate_enumeration(item)
    else:
        print "Item not handled for cy_generate", item
    #    raise ValueError, ("item not handled:", item)
