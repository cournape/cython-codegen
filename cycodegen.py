import sys
import re

from ctypeslib.codegen import typedesc
from tp_puller import TypePuller
from cython_gen import cy_generate
from misc import classify, query_items

def generate_cython(output, genitems, enumvals):
    # Generate the cython code
    cython_code = [cy_generate(i) for i in genitems]

    output.write("\tcdef enum:\n")
    for i in enumvals:
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
