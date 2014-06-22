from element_generation import generate_element
from fitter import fit_elements

import input_parse
import os, sys

me = os.path.dirname(__file__)

if __name__ == '__main__':
    
    if len(sys.argv) != 3:
        print "Usage: main.py inputFile(json) outputFile(schematic)"
        sys.exit(1)
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    
    print "Parsing input..."
    
    input_meta = input_parse.parse_input_file(input_file)
    
    gen = lambda x: generate_element(x, input_meta.input_color_key, input_meta.output_color_key)
    elements = list(gen(x) for x in input_meta.equations)

    final = fit_elements(input_meta, elements, OPTIONS = {"make_output_rail": True})
    
    final.saveToFile(output_file)

    print "Done"
    print "Input key:"
    print input_meta.get_input_color_key_with_names()
    print "Output key:"
    print input_meta.get_output_color_key_with_names()