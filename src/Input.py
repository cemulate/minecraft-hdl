import itertools
from block_constants import *



class Equation_META_INF(object):
    
    def __init__(self, name, inputs):
        self.name = name
        self.inputs = inputs
    
class SumOfProductsEquation(Equation_META_INF):
    
    def __init__(self, name, inputs, minterms):
        super(SumOfProductsEquation, self).__init__(name, inputs)
        self.minterms = minterms
        
    def __str__(self):
        return "[Equation(SoP) - " + self.name + " = f" + self.inputs
    
class AdditionEquation(Equation_META_INF):
    
    def __init__(self, name, inputs):
        super(AdditionEquation, self).__init__(name, inputs)
        
    def __str__(self):
        return "[Equation(Addition) - " + self.name + " = f" + self.inputs

class Input_META_INF(object):
    
    def __init__(self, input_domain, output_range, equations):
        self.input_domain = input_domain
        self.output_range = output_range
        self.input_color_key = None
        self.output_color_key = None
        self.equations = equations
    
    @property
    def equations(self):
        return self._equations

    @equations.setter
    def equations(self, value):
        self._equations = value
        self._generate_input_wool_color_key()
        self._generate_output_wool_color_key()

    def get_input_color_key_with_names(self):
        return {x : WOOL_NAMES[y] for x, y in list((i, self.input_color_key[i]) for i in self.input_color_key.keys())}
    
    def get_output_color_key_with_names(self):
        return {x : WOOL_NAMES[y] for x, y in list((i, self.output_color_key[i]) for i in self.output_color_key.keys())}
    
    
    
    def __str__(self):
        return "Input -- Combinational Equations: {0}".format(len(self.equations))
    
    def _generate_input_wool_color_key(self):
        key = dict(zip(self.input_domain, range(len(self.input_domain))))
        self.input_color_key = key
        
    def _generate_output_wool_color_key(self):
        names = list(x.name for x in self.equations)
        self.output_color_key = dict(zip(names, range(len(names))))