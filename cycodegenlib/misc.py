from ctypeslib.codegen import typedesc

#from ctypeslib.codegen.gccxmlparser import parse
from gccxmlparser import parse

def query_items(xml):
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

def classify(items, locations, lfilter=None):
    # Dictionaries name -> typedesc instances
    funcs = {}
    tpdefs = {}
    enumvals = {}
    enums = {}
    structs = {}
    vars = {}
    unions = {}

    if lfilter is None:
        lfilter = lambda x : True

    for it in items:
        try:
            origin = locations[it][0]
            if lfilter(origin):
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
