from element_generation import generate_element
from fitter import fit_elements

import input_parse
import os, sys

me = os.path.dirname(__file__)

if __name__ == '__main__':
    
    print "Parsing input..."
    
    if len(sys.argv) < 2:
        print "Please provide an input file"
    else:
        input_file = sys.argv[1]
    
    input_meta = input_parse.parse_input_file(input_file)
    
    gen = lambda x: generate_element(x, input_meta.input_color_key, input_meta.output_color_key)
    elements = list(gen(x) for x in input_meta.equations)

    final = fit_elements(input_meta, elements, OPTIONS = {"make_output_rail": True})
    
    final.saveToFile(os.path.join(me, "..", "final_fitter_out.schematic"))

    print "Done"
    print "Input key:"
    print input_meta.get_input_color_key_with_names()
    print "Output key:"
    print input_meta.get_output_color_key_with_names()