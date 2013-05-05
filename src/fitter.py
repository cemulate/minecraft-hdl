from __future__ import division

from pymclevel.schematic import MCSchematic
from pymclevel.box import BoundingBox
from pymclevel import alphaMaterials

from block_constants import *

def add_tuples(x, y):
    return tuple(sum(i) for i in zip(x, y))

def fit_elements(meta_input, element_list, OPTIONS):
    
    schematic_bufferX = 3
    #schematic_bufferZ = 4
    
    # Also, the schematics must be spaced out a certain length as well
    total_schematic_lengthX = sum(s.size[0] for s in element_list)
    sizeX = total_schematic_lengthX + schematic_bufferX * len(element_list) + 2
    
    sizeZ = element_list[0].size[2]
    sizeZ += 2 * max(len(meta_input.input_domain), len(meta_input.output_range)) + 6
    
    sizeY = max(s.size[1] for s in element_list) + 5
    
    level = MCSchematic(shape=(sizeX, sizeY, sizeZ))
    box = BoundingBox((0, 0, 0), (sizeX, sizeY, sizeZ))
    
    cx, cy, cz = 2, 0, 0
    
    schematic_origins = {}
    for s in element_list:
        
        schematic_origins[s] = [cx, cy, cz]
        
        level.copyBlocksFrom(s.schematic, BoundingBox((0, 0, 0), s.size), (cx, cy, cz))
        
        cx += s.size[0] + schematic_bufferX
    
    # The schematics contain their own *relative* input locations in a dict of the form
    # input name --> (x, y, z). We wish to make a giant composite list of all the *absolute* locations
    # of the inputs, this time of the form (x, y, z) --> input name. We obtain the absolute 
    # location by adding the individual schematic origin (in our coordinate system) with the 
    # schematic's relative coordinate.
    
    absolute_input_locations = {}
    for s in element_list:
        for key, value in s.relative_input_locations.items():
            abs_loc = add_tuples(schematic_origins[s], value)
            absolute_input_locations[abs_loc] = key
            
    # The z value for all the input locations will be the same. We just need to grab an arbitrary
    # one and use it to define the starting z location for the input rails
    
    input_z = 5 + absolute_input_locations.keys()[0][2]
    input_rail_z_values = {}
    for i in meta_input.input_domain:
        input_rail_z_values[i] = input_z
        input_z += 2
        
    absolute_output_locations = {}
    for s in element_list:
        for key, value in s.relative_output_locations.items():
            abs_loc = add_tuples(schematic_origins[s], value)
            absolute_output_locations[abs_loc] = key
        
    output_z = 4 + absolute_output_locations.keys()[0][2]
    output_rail_z_values = {}
    for i in meta_input.output_range:
        output_rail_z_values[i] = output_z
        output_z += 2
        
    
    # Step through the input locations and build backward to to the point where it joins
    # up with the appropriate input rail. The rail will actually be built later.
    
    for input_loc, input_name in absolute_input_locations.items():
        
        cx, cy, cz = input_loc[0], input_loc[1], input_loc[2]
        
        cz += 1
        
        while (cz < input_rail_z_values[input_name] - 1):
            level.setBlockAt(cx, cy, cz, REDSTONE)
            cz += 1
        
        level.setBlockAt(cx, cy, cz, REPEATER)
        
        cz += 1
        level.setBlockAt(cx, cy, cz, WOOL)
        level.setBlockDataAt(cx, cy, cz, meta_input.input_color_key[input_name])
        
        cy += 1
        level.setBlockAt(cx, cy, cz, REDSTONE)
        
    # Step through the output locations and build backward to to the point where it joins
    # up with the appropriate output rail. The rail will actually be built later.
    
    for output_loc, output_name in absolute_output_locations.items():
        
        if OPTIONS["make_output_rail"] == False:
            continue
        
        cx, cy, cz = output_loc[0], output_loc[1], output_loc[2]
        
        cz += 1
        
        while (cz < output_rail_z_values[output_name] - 1):
            level.setBlockAt(cx, cy, cz, REDSTONE)
            cy -= 1
            level.setBlockAt(cx, cy, cz, WOOL)
            level.setBlockDataAt(cx, cy, cz, meta_input.output_color_key[output_name])
            cy += 1
            cz += 1
        
        level.setBlockAt(cx, cy, cz, REPEATER)
        level.setBlockDataAt(cx, cy, cz, REPEATER_TOWARD_POS_Z)
        
        cy -= 1
        level.setBlockAt(cx, cy, cz, WOOL)
        level.setBlockDataAt(cx, cy, cz, meta_input.output_color_key[output_name])
        cy += 1
        
        cz += 1
        level.setBlockAt(cx, cy, cz, WOOL)
        level.setBlockDataAt(cx, cy, cz, meta_input.output_color_key[output_name])
        
        cy += 1
        level.setBlockAt(cx, cy, cz, REDSTONE)
            
    
    # Now build the input rails!
            
    for input_name, input_z_value in input_rail_z_values.items():
        cx, cy, cz = 0, 2, input_z_value
        while cx < sizeX:
            
            cy -= 1
            
            if level.blockAt(cx, cy, cz) != REDSTONE:
                level.setBlockAt(cx, cy, cz, WOOL)
                level.setBlockDataAt(cx, cy, cz, meta_input.input_color_key[input_name])
            level.setBlockAt(cx, cy, cz-1, WOOL)
            level.setBlockDataAt(cx, cy, cz-1, WOOL_BLACK)
            level.setBlockAt(cx, cy, cz+1, WOOL)
            level.setBlockDataAt(cx, cy, cz+1, WOOL_BLACK)
            
            cy += 1

            level.setBlockAt(cx, cy, cz, REDSTONE)
            
            cx += 1
    
    # We need to put repeaters on the input rail. There are multiple ways to do so. If POSSIBLE,
    # use the gap method. To do this we need to perform the following algorithm to find the 
    # gaps inbetween inputs.
    
    # Find the x values of the 'gaps' between clusters
    # of inputs. These are nice open spots to put repeaters. The following is a 'find the gap'
    # algorithm that ends up with a list of x values where repeaters should be placed (rep_locs)
    
    # Get the x values of the inputs
    input_x_values = list(x[0] for x in absolute_input_locations.keys())
    input_x_values.sort()
    
    # Get the differences between each pair of input x values
    diffs = list(input_x_values[i] - input_x_values[i-1] for i in range(1, len(input_x_values)))
    
    # Where these differences are more than 2, that means that we had a jump in the x values.
    # Obtain the indexes of the two input x values on either side of the jump
    gap_index_pairs = list((i, i+1) for i in range(len(diffs)) if diffs[i] > 2)
    
    
    # Finally, for each index pair, we want the x value in between the x values at those indices:
    # input_x_values[x] ---------------- (*) --------------- input_x_values[y] for each (x, y) pair in gap_index_pairs
    rep_locs = list(input_x_values[x] + int((input_x_values[y] - input_x_values[x]) / 2) for x, y in gap_index_pairs)
    
    
    # Now put repeaters on the input rail
    
    # We can get away with gap method if the rep_locs are within 15 spaces apart. Otherwise,
    # we'll HAVE to use an ugly-ass method
    
    rep_loc_spacings = list(rep_locs[i] - rep_locs[i-1] for i in range(1, len(rep_locs)))

    if len(rep_loc_spacings) > 0:
        rep_loc_max_spacing = max(rep_loc_spacings)
    else:
        # The method fails... just set max spacing to something ridiculous so that it does the other method
        rep_loc_max_spacing = 100
    
    if rep_loc_max_spacing <= 14:
        
        print "inputs - gap method"
        
        # GAP METHOD -- very nice looking, but doesn't work when the input domain is very large
        # because there *won't be any* gaps within 15 units, so it will place no repeaters.     
        
        cy = 2
        for iter_cx in rep_locs:
            for iter_cz in input_rail_z_values.values():
                level.setBlockAt(iter_cx, cy, iter_cz, REPEATER)
                level.setBlockDataAt(iter_cx, cy, iter_cz, REPEATER_TOWARD_POS_X)
                
    else:
        
        print "inputs - method 2"
    
        # Method 2 -- aesthetically displeasing... has to fudge around the block edges and produces
        # lines of repeaters with 'imperfections' from scooting the necessary ones 
        
        for input_name, input_z_value in input_rail_z_values.items():
            cx, cy, cz = 12, 2, input_z_value
            while cx < sizeX:
                if level.blockAt(cx, cy - 1, cz) == REDSTONE:
                    level.setBlockAt(cx - 2, cy, cz, REPEATER)
                    level.setBlockDataAt(cx - 2, cy, cz, REPEATER_TOWARD_POS_X)
                elif level.blockAt(cx - 1, cy - 1, cz) == REDSTONE:
                    level.setBlockAt(cx + 1, cy, cz, REPEATER)
                    level.setBlockDataAt(cx + 1, cy, cz, REPEATER_TOWARD_POS_X)
                elif level.blockAt(cx + 1, cy - 1, cz) == REDSTONE:
                    level.setBlockAt(cx - 1, cy, cz, REPEATER)
                    level.setBlockDataAt(cx - 1, cy, cz, REPEATER_TOWARD_POS_X)
                else:
                    level.setBlockAt(cx, cy, cz, REPEATER)
                    level.setBlockDataAt(cx, cy, cz, REPEATER_TOWARD_POS_X)
                cx += 12
                
                      
            
            
    
    if OPTIONS["make_output_rail"]:
          
        # Now build the output rails!
        
        outputHeight = absolute_output_locations.keys()[0][1] + 2
        
        for output_name, output_z_value in output_rail_z_values.items():
            
            cx, cy, cz = 0, outputHeight, output_z_value
            while cx < sizeX:
                
                cy -= 1
                
                if level.blockAt(cx, cy, cz) != REDSTONE:
                    level.setBlockAt(cx, cy, cz, WOOL)
                    level.setBlockDataAt(cx, cy, cz, meta_input.output_color_key[output_name])
                level.setBlockAt(cx, cy, cz-1, WOOL)
                level.setBlockDataAt(cx, cy, cz-1, WOOL_BLACK)
                level.setBlockAt(cx, cy, cz+1, WOOL)
                level.setBlockDataAt(cx, cy, cz+1, WOOL_BLACK)
                
                cy += 1
                
                level.setBlockAt(cx, cy, cz, REDSTONE)
                
                cx += 1
        
        # We need to find gaps for the gap method again
        
        output_x_values = list(x[0] for x in absolute_output_locations.keys())
        output_x_values.sort()
        
        diffs = list(output_x_values[i] - output_x_values[i-1] for i in range(1, len(output_x_values)))
        
        gap_index_pairs = list((i, i+1) for i in range(len(diffs)) if diffs[i] > 2)
        
        rep_locs = list(output_x_values[x] + int((output_x_values[y] - output_x_values[x]) / 2) for x, y in gap_index_pairs)
        
        
        if len(rep_loc_spacings) > 0:
            rep_loc_max_spacing = max(rep_loc_spacings)
        else:
            # The method fails... just set max spacing to something ridiculous so that it does the other method
            rep_loc_max_spacing = 100
        
        if rep_loc_max_spacing < 14:
            
            print "outputs - gap method"
            
            # GAP METHOD -- very nice looking, but doesn't work when the input domain is very large
            # because there *won't be any* gaps within 15 units, so it will place no repeaters.     
            
            cy = outputHeight
            for iter_cx in rep_locs:
                for iter_cz in output_rail_z_values.values():
                    level.setBlockAt(iter_cx, cy, iter_cz, REPEATER)
                    level.setBlockDataAt(iter_cx, cy, iter_cz, REPEATER_TOWARD_NEG_X)
                    
        else:
            
            print "outputs - method 2"
            
            # Method 2 -- aesthetically displeasing... has to fudge around the block edges and produces
            # lines of repeaters with 'imperfections' from scooting the necessary ones 
            
            for output_name, output_z_value in output_rail_z_values.items():
                cx, cy, cz = 12, outputHeight, output_z_value
                while cx < sizeX:
                    if level.blockAt(cx, cy - 1, cz) == REDSTONE:
                        level.setBlockAt(cx - 2, cy, cz, REPEATER)
                        level.setBlockDataAt(cx - 2, cy, cz, REPEATER_TOWARD_NEG_X)
                    elif level.blockAt(cx - 1, cy - 1, cz) == REDSTONE:
                        level.setBlockAt(cx + 1, cy, cz, REPEATER)
                        level.setBlockDataAt(cx + 1, cy, cz, REPEATER_TOWARD_NEG_X)
                    elif level.blockAt(cx + 1, cy - 1, cz) == REDSTONE:
                        level.setBlockAt(cx - 1, cy, cz, REPEATER)
                        level.setBlockDataAt(cx - 1, cy, cz, REPEATER_TOWARD_NEG_X)
                    else:
                        level.setBlockAt(cx, cy, cz, REPEATER)
                        level.setBlockDataAt(cx, cy, cz, REPEATER_TOWARD_NEG_X)
                    cx += 12
    
    return level
    
    