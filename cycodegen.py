import sys
import re
import copy

#from ctypeslib.codegen.gccxmlparser import parse
from gccxmlparser import parse
from ctypeslib.codegen import typedesc
from codegenlib import Func, parse_type
from funcs import generic_as_arg
from cytypes import generic_decl, generic_named_decl

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
            named[it] = it.name

        if hasattr(it, 'location'):
            locations[it] = it.location

    return keep, named, locations

def classify(items, locations, ifilter=None):
    # Dictionaries name -> typedesc instances
    funcs = {}
    tpdefs = {}
    enumvals = {}
    enums = {}
    structs = {}
    vars = {}
    unions = {}

    if ifilter is None:
        ifilter = lambda x : True

    for it in items:
        try:
            origin = locations[it][0]
            if ifilter(origin):
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
                elif isinstance(it, typedesc.Union):
                    unions[it.name] = it
                else:
                    print "Do not know how to classify", str(it)
        except KeyError:
            if isinstance(it, typedesc.EnumValue):
                enumvals[it.name] = it
            else:
                print "No location for item %s, ignoring" % str(it)

    return funcs, tpdefs, enumvals, enums, structs, unions, vars

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

def signatures_types(funcs):
    """Given a sequence of typedesc.Function instances, generate a set of all
    typedesc instances used in function declarations."""
    arguments = set()

    for f in funcs:
        for t in f.iterArgTypes():
            ut = find_unqualified_type(t)
            if ut in items:
                arguments.add(ut)
        ut = find_unqualified_type(f.returns)
        if ut in items:
            arguments.add(ut)

    return arguments

class TypePuller:
    def __init__(self, all):
        self._items = []
        #self._all = sorted(all, cmpitems)
        self._all = all
        self._done = set()

        # This list contains a list of struct names for which the puller will
        # not pull the members. This is an hack to avoid some cycle in
        # recursives structs declarations which refer one to each other.
        self._STRUCTS_IGNORE = ['_IO_FILE', '_IO_marker', 'yoyo11', 'yoyo12']

    def pull_fundamental(self, item):
        pass

    def pull_cv_qualified_type(self, item):
        self.pull(item.typ)
        #names.add(item.name)
        self._items.append(item)

    def pull_typedef(self, item):
        # XXX: Generate the typdef itself
        if not item in self._done:
            self._done.add(item)
            self.pull(item.typ)
            #names.add(item.name)
            self._items.append(item)

    def pull_function(self, item):
        # XXX: fix signatures_type for single item
        types = signatures_types([item])
        #names.append(item.name)
        for t in types:
            ut = find_unqualified_type(t)
            if ut in self._all:
                self.pull(ut)
        self._items.append(item)

    def pull_function_type(self, item):
        # XXX: fix signatures_type for single item
        types = signatures_types([item])
        #self._items.append(item)
        for t in types:
            ut = find_unqualified_type(t)
            if ut in self._all:
                self.pull(ut)

    def pull_structure(self, item):
        #names.append(item.name)
        if not item in self._done:
            self._done.add(item)
            if item.name in self._STRUCTS_IGNORE:
                # XXX: hack. We remove all members of the ignored structures,
                # to generate an opaque structure in the code genrator.
                print "Ignoring", item, item.name
                item.members = []
            else:
                for m in item.members:
                    if isinstance(m, typedesc.Field):
                        f = m.typ
                        # XXX: ugly hack. Cython does not support structures
                        # with members refering to itself through a typedef, so
                        # we "untypedef" the member if we detect such a case
                        if isinstance(f, typedesc.PointerType) \
                           and isinstance(f.typ, typedesc.Typedef) \
                           and isinstance(f.typ.typ, typedesc.Structure) \
                           and f.typ.typ == item:
                            newf = copy.deepcopy(f)
                            newf.typ = newf.typ.typ
                            m.typ = newf
                    self.pull(m)
            self._items.append(item)

    def pull_union(self, item):
        #names.append(item.name)
        for m in item.members:
            g = self.pull(m)
            if g:
                self._items.append(pull(m))
        self._items.append(item)

    def pull_array_type(self, item):
        #names.append(item.name)
        self.pull(item.typ)
        self._items.append(item)

    def pull_enumeration(self, item):
        #names.append(item.name)
        for v in item.values:
            self.pull(v)
        self._items.append(item)

    def pull_enum_value(self, item):
        #names.append(item.name)
        self._items.append(item)

    def pull(self, item):
        if isinstance(item, typedesc.FundamentalType):
            #print "Fund Pulling", item, item.name
            self.pull_fundamental(item)
            return
        elif isinstance(item, typedesc.Enumeration):
            #print "Enumeration Pulling", item, item.name
            self.pull_enumeration(item)
            return
        elif isinstance(item, typedesc.EnumValue):
            #print "Enumeration Pulling", item, item.name
            self.pull_enum_value(item)
            return
        elif isinstance(item, typedesc.Typedef):
            #print "Typedef Pulling", item, item.name
            self.pull_typedef(item)
            return
        elif isinstance(item, typedesc.Structure):
            #print "Struct Pulling", item, item.name
            self.pull_structure(item)
            return
        elif isinstance(item, typedesc.Union):
            #print "FunctionType Pulling", item
            self.pull_union(item)
            return
        elif isinstance(item, typedesc.Function):
            #print "Func Pulling", item
            self.pull_function(item)
            return
        elif isinstance(item, typedesc.Field):
            #print "Field Pulling", item
            self.pull(item.typ)
            return
        elif isinstance(item, typedesc.PointerType):
            #print "Pointer Pulling", item
            self.pull(item.typ)
            return
        elif isinstance(item, typedesc.FunctionType):
            #print "FunctionType Pulling", item
            self.pull_function_type(item)
            return
        elif isinstance(item, typedesc.CvQualifiedType):
            #print "FunctionType Pulling", item
            self.pull_cv_qualified_type(item)
            return
        elif isinstance(item, typedesc.ArrayType):
            #print "FunctionType Pulling", item
            self.pull_array_type(item)
            return
        else:
            raise ValueError, ("item not handled:", item)

    def values(self):
        return self._items

def instance_puller(tp, all):
    p = TypePuller(all)
    p.pull(tp)
    return p.values()

def cmpitems(a, b):
    aloc = getattr(a, "location", None)
    bloc = getattr(b, "location", None)
    if aloc is None:
        return -1
    if bloc is None:
        return 1

    st = cmp(aloc[0],bloc[0]) or cmp(int(aloc[1]),int(bloc[1]))
    if st == 0:
        # Two items as the same location: if it is a typedef'd structure with
        # different name and tag, we make sure the structure is defined before
        # the typedef. If it is a different case, just do nothing for now
        if isinstance(a, typedesc.Structure):
            if isinstance(b, typedesc.Typedef):
                return -1
            else:
                # XXX
                print "Hm, not sure what to do here"
                return 0
        if isinstance(b, typedesc.Structure):
            if isinstance(a, typedesc.Typedef):
                return 1
            else:
                print "Hm, not sure what to do here"
                return 0
    else:
        return st

def named_pointer_decl(tp):
    if isinstance(tp.typ, typedesc.FunctionType):
        args = [generic_decl(arg) for arg in tp.typ.iterArgTypes()]
        return generic_decl(tp.typ.returns) + '(*%s)' + '(%s)' % ", ".join(args)
    else:
        return generic_decl(tp.typ) + ' * %s'

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

#root = 'asoundlib'
#root = 'CoreAudio_AudioHardware'
root = 'foo'
header_name = '%s.h' % root
#header_matcher = re.compile('alsa')
header_matcher = re.compile(header_name)
#header_matcher = re.compile('AudioHardware')
xml_name = '%s.xml' % root
pyx_name = '_%s.pyx' % root
if sys.platform[:7] == 'darwin':
    so_name = root
else:
    so_name = 'lib%s.so' % root

items, named, locations = query_items(xml_name)
funcs, tpdefs, enumvals, enums, structs, vars, unions = \
        classify(items, locations, ifilter=header_matcher.search)

arguments = signatures_types(funcs.values())
#print "Need to pull out arguments", [named[i] for i in arguments]

puller = TypePuller(items)
for a in arguments:
    puller.pull(a)

needed = puller.values()
#print "Pulled out items:", [named[i] for i in needed]

# Order 'anonymous' enum values alphabetically
def cmpenum(a, b):
    return cmp(a.name, b.name)
anoenumvals = enumvals.values()
anoenumvals.sort(cmpenum)

# List of items to generate code for
#gen = enumvals.values() + list(needed) + funcs.values()
gen = list(needed) + funcs.values()

#gen_names = [named[i] for i in gen]

cython_code = [cy_generate(i) for i in gen]

output = open(pyx_name, 'w')
output.write("cdef extern from '%s':\n" % header_name)
output.write("\tcdef enum:\n")
for i in anoenumvals:
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
output.close()
