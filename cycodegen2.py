import sys
import re

#from ctypeslib.codegen.gccxmlparser import parse
from gccxmlparser import parse
from ctypeslib.codegen import typedesc
from codegenlib import Func, parse_type

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

def classify(items, locations):
    # Dictionaries name -> typedesc instances
    funcs = {}
    tpdefs = {}
    enumvals = {}
    enums = {}
    structs = {}
    vars = {}

    for it in items:
        try:
            origin = locations[it][0]
            if header_matcher.search(origin):
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

    return funcs, tpdefs, enumvals, enums, structs, vars

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

def signatures_types(funcs):
    """Given a sequence of typedesc.Function instances, generate a set of all
    typedesc instances used in function declarations."""
    arguments = set()

    for f in funcs:
        for t in f.iterArgTypes():
            ut = find_unqualified_type(t)
            if ut in items:
                arguments.add(ut)

    return arguments

class TypePuller:
    def __init__(self, all):
        self._items = set()
        self._all = all

    def pull_fundamental(self, item):
        pass

    def pull_cv_qualified_type(self, item):
        self.pull(item.typ)
        #names.add(item.name)
        self._items.add(item)

    def pull_typedef(self, item):
        # XXX: Generate the typdef itself
        self.pull(item.typ)
        #names.add(item.name)
        self._items.add(item)

    def pull_function(self, item):
        # XXX: fix signatures_type for single item
        types = signatures_types([item])
        self._items.add(item)
        #names.add(item.name)
        for t in types:
            ut = find_unqualified_type(t)
            if ut in self._all:
                self._items.add(ut)

    def pull_function_type(self, item):
        # XXX: fix signatures_type for single item
        types = signatures_types([item])
        #self._items.add(item)
        for t in types:
            ut = find_unqualified_type(t)
            if ut in self._all:
                self._items.add(ut)

    def pull_structure(self, item):
        self._items.add(item)
        #names.add(item.name)
        for m in item.members:
            g = self.pull(m)
            if g:
                self._items.add(pull(m))

    def pull(self, item):
        if isinstance(item, typedesc.FundamentalType):
            #print "Fund Pulling", item
            self.pull_fundamental(item)
            return
        elif isinstance(item, typedesc.Typedef):
            #print "Typedef Pulling", item
            self.pull_typedef(item)
            return
        elif isinstance(item, typedesc.Structure):
            #print "Struct Pulling", item, item.name
            self.pull_structure(item)
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
        else:
            raise ValueError, ("item not handled:", item)

    def values(self):
        return self._items

root = 'foo'
header_name = '%s.h' % root
header_matcher = re.compile(header_name)
xml_name = '%s.xml' % root
if sys.platform[:7] == 'darwin':
    so_name = root
else:
    so_name = 'lib%s.so' % root

items, named, locations = query_items(xml_name)
funcs, tpdefs, enumvals, enums, structs, vars = classify(items, locations)

arguments = signatures_types(funcs.values())
print "Need to pull out arguments", [named[i] for i in arguments]

puller = TypePuller(items)
for a in arguments:
    puller.pull(a)

needed = puller.values()
print "Pulled out items:", [named[i] for i in needed]
