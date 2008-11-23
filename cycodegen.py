from ctypeslib.codegen.gccxmlparser import parse
from ctypeslib.codegen import typedesc

header_name = 'alsa/asoundlib.h'
xml_name = 'asoundlib.xml'

header_name = 'foo.h'
xml_name = 'foo.xml'
so_name = 'libfoo.so'

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
#keep = [it for it in items if (isinstance(it, typedesc.Function) and it.name.startswith('snd_card'))]
#keep = [it for it in items if isinstance(it, typedesc.Function)]
keep = items

class Func:
    def __init__(self, ret, name, args):
        self.name = name
        self.returns = ret
        self.args = args

    def signature(self):
        return "%s %s(%s)" % (self.returns, self.name, ",".join(self.args))

def parse_type(tp):
    if isinstance(tp, typedesc.FundamentalType):
        return tp.name
    elif isinstance(tp, typedesc.PointerType):
        return parse_type(tp.typ) + '*'
    elif isinstance(tp, typedesc.CvQualifiedType):
        return 'const ' + parse_type(tp.typ)
    elif isinstance(tp, typedesc.Typedef):
        return '%s %s %s' % ('typedef', tp.name, parse_type(tp.typ))
    else:
        raise ValueError("yoyo", type(tp))

def parse_enum(tp):
    return tp.name + ' ' + tp.value

funcs = []
for k in keep:
    if isinstance(k, typedesc.Function):
        if syms.has(k.name):
            print k.name
            for arg in k.iterArgTypes():
                print '\t',  parse_type(arg)
    #funcs.append(Func(k.returns.name, k.name, args_type))
    elif isinstance(k, typedesc.EnumValue):
        print parse_enum(k)
    elif isinstance(k, typedesc.Typedef):
        print '%s %s %s' % ('typedef', k.name, parse_type(k.typ))
    elif isinstance(k, typedesc.Structure):
        print 'struct: %s' % k.name
        for f in k.members:
            print '\t' + f.name + ': ' + parse_type(f.typ)
    else:
        print "Do not know how to handle", str(k)

#def codegen(syms):
#    output = []
#    output.append('cdef extern from "%s":' % header_name)
#    indent = '    '
#    for s in syms:
#        output.append(indent + s.signature())
#
#    print '\n'.join(output)
#
#codegen(funcs)
