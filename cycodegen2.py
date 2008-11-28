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
keep = [it for it in items if (hasattr(it, 'name') and it.name and not it.name.startswith('__'))]

funcs = {}
tpdefs = {}
enumvals = {}
enums = {}
structs = {}
vars = {}
for k in keep:
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

for name, f in funcs.items():
    print "Generating decl for func %s" % name
    args = [generic_as_arg(a) for a in f.iterArgTypes()]
    print args
