import sys

from ctypeslib.codegen.gccxmlparser import parse
from ctypeslib.codegen import typedesc
from codegenlib import Func, parse_type

root = 'foo'
header_name = '%s.h' % root
xml_name = '%s.xml' % root
if sys.platform[:7] == 'darwin':
    so_name = root
else:
    so_name = 'lib%s.so' % root

items = parse(xml_name)
#keep = [it for it in items if (hasattr(it, 'name') and it.name and not it.name.startswith('__'))]
keep = items

# Dictionaries name -> typedesc instances
funcs = {}
tpdefs = {}
enumvals = {}
enums = {}
structs = {}
vars = {}

# Dictionary name -> location (as integer)
locations = {}

# List of items used as function argument
arguments = {}

for k in keep:
    # Location computation only works when all definitions/declarations are
    # pulled from one header.
    if hasattr(k, 'name') and hasattr(k, 'location'):
        locations[k.name] = int(k.location[1])
    if isinstance(k, typedesc.Function):
        funcs[k.name] = k
    elif isinstance(k, typedesc.EnumValue):
        enumvals[k.name] = k
    elif isinstance(k, typedesc.Enumeration):
        enums[k.name] = k
    elif isinstance(k, typedesc.Typedef):
        tpdefs[k.name] = k
    elif isinstance(k, typedesc.Structure):
        structs[k.name] = k
    elif isinstance(k, typedesc.Variable):
        vars[k.name] = k
    else:
        print "Do not know how to handle", str(k)

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

for name, f in funcs.items():
    #print "Generating decl for func %s" % name
    args = [generic_as_arg(a) for a in f.iterArgTypes()]
    for a in f.iterArgTypes():
        namedtype = find_named_type(a)
        if namedtype:
            arguments[namedtype] = None

    print "%s %s(%s)" % (generic_as_arg(f.returns), name, ", ".join(args))
