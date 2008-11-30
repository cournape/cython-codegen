import sys
import re

#from ctypeslib.codegen.gccxmlparser import parse
from gccxmlparser import parse
from ctypeslib.codegen import typedesc
from codegenlib import Func, parse_type

root = 'foo'
header_name = '%s.h' % root
header_matcher = re.compile(header_name)
xml_name = '%s.xml' % root
if sys.platform[:7] == 'darwin':
    so_name = root
else:
    so_name = 'lib%s.so' % root

def query_items(xml, filter=None):
    # XXX: support filter
    xml_items = parse(xml)
    #items = {}
    keep = set()
    named = {}
    locations = {}
    for it in xml_items:
        #items[it] = it
        keep.add(it)

        if hasattr(it, 'name'):
            named[it.name] = it

        if hasattr(it, 'location'):
            locations[it] = it.location

    return keep, named, locations

items, named, locations = query_items(xml_name)

# Dictionaries name -> typedesc instances
funcs = {}
tpdefs = {}
enumvals = {}
enums = {}
structs = {}
vars = {}

# List of items used as function argument
arguments = {}

# List of items we may use and can handle
handled = {}

for it in items:
    try:
        origin = locations[it][0]
        if header_matcher.search(origin):
            if hasattr(it, 'name'):
                handled[it.name] = it
            if isinstance(it, typedesc.Function):
                funcs[it.name] = it
            elif isinstance(it, typedesc.EnumValue):
                enumvals[it.name] = it
            elif isinstance(it, typedesc.Enumeration):
                enums[it.name] = it
            elif isinstance(it, typedesc.Typedef):
                tpdefs[it.name] = it
            elif isinstance(it, typedesc.Structure):
                structs[it.name] = it
            elif isinstance(it, typedesc.Variable):
                vars[it.name] = it
            else:
                print "Do not itnow how to handle", str(it)
    except KeyError:
        print "No location for item %s, ignoring" % str(it)

from funcs import generic_as_arg

def find_named_type(tp):
    if hasattr(tp, 'name'):
        return tp.name
    elif isinstance(tp, typedesc.CvQualifiedType) or \
         isinstance(tp, typedesc.PointerType):
        return find_named_type(tp.typ)
    elif isinstance(tp, typedesc.FunctionType):
        return None
    else:
        raise ValueError("Unhandled type %s" % str(tp))

def find_unqualified_type(tp):
    if isinstance(tp, typedesc.FundamentalType) or \
            isinstance(tp, typedesc.Structure) or \
            isinstance(tp, typedesc.Typedef):
        return tp
    elif isinstance(tp, typedesc.CvQualifiedType) or \
         isinstance(tp, typedesc.PointerType):
        return find_unqualified_type(tp.typ)
    elif isinstance(tp, typedesc.FunctionType):
        return None
    else:
        raise ValueError("Unhandled type %s" % str(tp))

def signature_types(func):
    types = []
    for a in func.iterArgTypes():
        #namedtype = find_named_type(a)
        #if namedtype:
        #    types.append(namedtype)
        types.append(a)

    return types

for name, f in funcs.items():
    types = signature_types(f)
    for t in types:
        ut = find_unqualified_type(t)
        if ut in items:
            arguments[ut] = None

print "Need to pull out arguments", arguments.keys()

from cytypes import generic_decl, generic_def

print "========== declarations ============="
for a in arguments.keys():
    print generic_decl(a)
    #if isinstance(a, typedesc.Typedef):
    #    print generic_decl(a.typ)

print "========== definitions ============="
for a in arguments.keys():
    print generic_def(a)
    if isinstance(a, typedesc.Typedef):
        print generic_def(a.typ)

print "============================="
print structs
