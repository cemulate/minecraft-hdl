class Element(object):
    
    def __init__(self):
        self.schematic = None
        self.relative_output_locations = None
        self.relative_input_locations = None
        self.size = None
    
class CombinationalElement(Element):
    
    def __init__(self, schematic):
        self.schematic = schematic
        self.relative_output_locations = None
        self.relative_input_locations = None
        self.size = None
        
class AdditionElement(Element):
    
    def __init__(self, schematic):
        self.schematic = schematic
        self.relative_output_locations = None
        self.relative_input_locations = None
        self.size = None