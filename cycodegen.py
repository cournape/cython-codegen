import os

from ctypeslib.codegen.gccxmlparser import parse
from ctypeslib.codegen import typedesc
from codegenlib import Func, parse_type

#header_name = 'alsa/asoundlib.h'
#xml_name = 'asoundlib.xml'

header_name = 'foo.h'
xml_name = 'foo.xml'
if os.name[:7] == 'darwin':
    so_name = 'foo'
else:
    so_name = 'libfoo.so'

#header_name = 'sndfile.h'
#xml_name = 'sndfile.xml'
#so_name = 'libsndfile.dylib'

class LibrarySymbols:
    def __init__(self, soname):
        from ctypes import CDLL
        self.lib = CDLL(soname)

    def __getitem__(self, name):
        try:
            return self.lib[name]
        except AttributeError, e:
            raise KeyError("Symbols %s not found", name)

    def has(self, name):
        try:
            self.lib[name]
            return True
        except AttributeError:
            return False


items = parse(xml_name)
syms = LibrarySymbols(so_name)
#symbols = ['foo', 'foof', 'fool']
#keep = [it for it in items if (isinstance(it, typedesc.Function) and it.name.startswith('sf_'))]
keep = [it for it in items if (it.name and not it.name.startswith('__'))]
#keep = [it for it in items if isinstance(it, typedesc.Function)]
#keep = items

def parse_enum(tp):
    return tp.name, tp.value

funcs = {}
tpdefs = {}
enumvals = {}
enums = []
structs = {}
for k in keep:
    if isinstance(k, typedesc.Function):
        if syms.has(k.name) :#and k.name.startswith("sf_"):
            funcs[k.name] = Func(k)
    #funcs.append(Func(k.returns.name, k.name, args_type))
    elif isinstance(k, typedesc.EnumValue):
        name, value = parse_enum(k)
        enumvals[name] = value
    elif isinstance(k, typedesc.Enumeration):
        enums.append(k)
    elif isinstance(k, typedesc.Typedef):
        tpdefs[k.name] = parse_type(k.typ)
        #print '%s %s %s' % ('typedef', k.name, parse_type(k.typ))
    elif isinstance(k, typedesc.Structure):
        #print 'struct: %s' % k.name
        #for f in k.members:
        #    print '\t' + f.name + ': ' + parse_type(f.typ)
        structs[k.name] = k.members
    elif isinstance(k, typedesc.Variable):
        #print 'struct: %s' % k.name
        #for f in k.members:
        #    print '\t' + f.name + ': ' + parse_type(f.typ)
        print k.name
    else:
        print "Do not know how to handle", str(k)

def parse_type_definition(tp):
    if isinstance(tp, typedesc.FundamentalType):
        return tp.name
    elif isinstance(tp, typedesc.PointerType):
        return parse_type(tp.typ) + '*'
    elif isinstance(tp, typedesc.CvQualifiedType):
        return 'const ' + parse_type(tp.typ)
    elif isinstance(tp, typedesc.Structure):
        return tp.name
    elif isinstance(tp, typedesc.FunctionType):
        return ""
    else:
        raise ValueError("yoyo", type(tp))

#Def generate_typedef_declaration(tp):
#    return "typedef %s %s" % (tp.name, tp.typ)

def codegen(decls):
    output = []
    output.append('cdef extern from "%s":' % header_name)
    indent = '    '
    for d in decls.values():
        output.append(indent + d.signature())

    print '\n'.join(output)

codegen(funcs)
