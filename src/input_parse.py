import itertools
import Input

import json

from block_constants import *

def parse_input_file(infile):

    obj = json.load(open(infile))
    
    input_domain = obj['inputs']
    output_range = obj['outputs']

    equations = []

    for eq in obj['equations']:

        eq = ''.join(x for x in eq if x.isalpha() or x in ['~', '|', '&', '='])
        lhs, rhs = eq.split('=')

        name = lhs

        inputs = list(set(x for x in rhs if x.isalpha()))
        inputs.sort()

        terms = []
        
        imps = rhs.split('|')
        for i in imps:
            imp_dict = {}
            
            vars = i.split('&')
            for v in vars:
                if '~' in v:
                    v = v.replace('~', '')
                    imp_dict[v] = 0
                else:
                    imp_dict[v] = 1
            
            terms.append(imp_dict)
            
        equations.append(Input.SumOfProductsEquation(name, inputs, terms))


    return Input.Input_META_INF(input_domain, output_range, equations)