import copy

from ctypeslib.codegen import typedesc
from funcs import find_unqualified_type

def _signatures_types(funcs, items):
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
        types = _signatures_types([item], self._all)
        #names.append(item.name)
        for t in types:
            ut = find_unqualified_type(t)
            if ut in self._all:
                self.pull(ut)
        self._items.append(item)

    def pull_function_type(self, item):
        # XXX: fix signatures_type for single item
        types = _signatures_types([item], self._all)
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

