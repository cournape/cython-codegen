import sys
import re

#from ctypeslib.codegen.gccxmlparser import parse
from gccxmlparser import parse
from ctypeslib.codegen import typedesc
from codegenlib import Func, parse_type
from tp_puller import TypePuller
from cython_gen import cy_generate

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

#arguments = signatures_types(funcs.values())
#print "Need to pull out arguments", [named[i] for i in arguments]

puller = TypePuller(items)
for f in funcs.values():
    puller.pull(f)

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
