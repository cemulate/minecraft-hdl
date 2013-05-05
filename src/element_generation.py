from Input import *
import combinational_element_factory
import addition_element_factory    
        
def generate_element(equation, use_input_color_key = None, use_output_color_key = None):
    
    if type(equation) is SumOfProductsEquation:
        return combinational_element_factory.generate(equation, use_input_color_key, use_output_color_key)
    
    elif type(equation) is AdditionEquation:
        return addition_element_factory.generate(equation, use_input_color_key, use_output_color_key)