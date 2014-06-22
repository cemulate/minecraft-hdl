from __future__ import division
import os, math

me = os.path.dirname(__file__)
from block_constants import *
from Element import CombinationalElement

from pymclevel.schematic import MCSchematic
from pymclevel.box import BoundingBox
from pymclevel import alphaMaterials

form_tall = MCSchematic(filename=os.path.join(me, "..", "res", "generic_boolean_blank.schematic"))
form_short = MCSchematic(filename=os.path.join(me, "..", "res", "generic_boolean_short_blank.schematic"))
formBox_tall = BoundingBox((0, 0, 0), (form_tall.Width, form_tall.Height, form_tall.Length))
formBox_short = BoundingBox((0, 0, 0), (form_short.Width, form_short.Height, form_short.Length))



def generate(comb_equation, use_input_color_key = None, use_output_color_key = None):
    
    inputs = comb_equation.inputs
    minterms = comb_equation.minterms
    
    form = form_tall if len(minterms) > 5 else form_short
    formBox = formBox_tall if len(minterms) > 5 else formBox_short
    implicantLimit = 13 if len(minterms) > 5 else 5
    
    
    while len(minterms) % implicantLimit != 0:
        minterms.append({})

    numXCopies = int(math.ceil(len(inputs) / 4))
    sizeX = numXCopies * form.Width + 2
    numYCopies = int(math.ceil(len(minterms) / implicantLimit))
    sizeY = numYCopies * form.Height + 3
    sizeZ = form.Length + 1

#    print sizeX, sizeY, sizeZ

    level = MCSchematic(shape=(sizeX, sizeY, sizeZ))
    box = BoundingBox((0, 0, 0), (sizeX, sizeY, sizeZ))


    # ================================================================================================


    # Paste the schematic the number of times we know we'll need

    pasteX = 0
    for i in range(numXCopies):
        pasteY = 1
        for i in range(numYCopies):
            level.copyBlocksFrom(form, formBox, (pasteX, pasteY, 0))
            pasteY += form.Height
        pasteX += form.Width


    # Fill the bottom plane with a ground
    
    # level.fillBlocks(BoundingBox((0, 0, 0), (sizeX, 1, sizeZ)), alphaMaterials.BlockofIron)
    

    # Build X-ways across each row corresponding to each term

    cx = 0
    cy = 2
    cz = 1
    numTerms = 0
    side = CLOSE_SIDE
    
    relative_input_locations = {}
    
    for termIndex in range(len(minterms)):
        
        term = minterms[termIndex]
        
        cx = 0
        for i in inputs:

            if i in term.keys():
                mat = TORCH if term[i] else REDSTONE
            else:
                mat = AIR

            data = TORCH_POINTING_NEG_Z if (cz == 1) else TORCH_POINTING_POS_Z

            level.setBlockAt(cx, cy, cz, mat)
            level.setBlockDataAt(cx, cy, cz, data)
            
            if termIndex == 0:
                sx = cx
                sy = cy - 2
                sz = cz + 4
                for iter_sz in [sz, sz+1, sz+2, sz+3]:
                    level.setBlockAt(sx, sy, iter_sz, WOOL)
                    data = WOOL_BLACK if use_input_color_key == None else use_input_color_key[i]
                    level.setBlockDataAt(sx, sy, iter_sz, data)
                    
                relative_input_locations[i] = [sx, sy, sz+2]

            cx += 2


        # Build the slice of the side scaffolding that goes on this row's height level:
        # -----------------------------------------------------------------------------
        prevCy = cy
        prevCz = cz

        cx = box.width - 2

        if side == CLOSE_SIDE:
            cz -= 1
            cy -= 1
        elif side == FAR_SIDE:
            cz += 1
            cy -= 1

        if len(term) > 0:
            level.setBlockAt(cx, cy, cz, TORCH)
            level.setBlockDataAt(cx, cy, cz, TORCH_POINTING_POS_X)

        cx += 1
        cy -= 1

        if numTerms in [0, 1]:
            level.setBlockAt(cx, cy, cz, DOUBLE_SLAB)
            level.setBlockDataAt(cx, cy, cz, DOUBLE_SLAB_STONE)
        else:
            level.setBlockAt(cx, cy, cz, SLAB)
            level.setBlockDataAt(cx, cy, cz, STONE_SLAB_TOP)

        cy += 1

        level.setBlockAt(cx, cy, cz, REDSTONE)

        if side == CLOSE_SIDE:
            cz += 1
        elif side == FAR_SIDE:
            cz -= 1

        level.setBlockAt(cx, cy, cz, SLAB)
        level.setBlockDataAt(cx, cy, cz, STONE_SLAB_TOP)

        cy += 1

        level.setBlockAt(cx, cy, cz, REDSTONE)

        if side == CLOSE_SIDE:
            currentCloseTowerTopY = cy
            currentCloseTowerTopZ = cz
        elif side == FAR_SIDE:
            currentFarTowerTopY = cy
            currentFarTowerTopZ = cz

        cy = prevCy
        cz = prevCz
        # -----------------------------------------------------------------------------


        # Switch sides

        side = FAR_SIDE if (side == CLOSE_SIDE) else CLOSE_SIDE

        # The z location alternates depending on the side

        if side == CLOSE_SIDE: cz = 1
        if side == FAR_SIDE: cz = 8

        # Keep track of the number of terms

        numTerms += 1

        # JUMP LOGIC
        # Normal case: cy goes up by one, we are working term by term up one paste of the schematic
        # Special case: We have done 13 terms, and need to 'jump' to the next paste of the schematic
        #    This requires some special connecting and bridging.

        # ------------------------------------------------------------------------------------------
        if numTerms == implicantLimit:

            sx = box.width - 1
            sy = currentCloseTowerTopY
            sz = currentCloseTowerTopZ

            sz += 1

            level.setBlockAt(sx, sy, sz, WOOL)
            level.setBlockDataAt(sx, sy, sz, WOOL_BLACK)

            sz += 1

            level.setBlockAt(sx, sy, sz, TORCH)
            level.setBlockDataAt(sx, sy, sz, TORCH_POINTING_POS_Z)

            sy += 1

            for itr_sz in [sz, sz-1, sz-2]:
                level.setBlockAt(sx, sy, itr_sz, WOOL)
                level.setBlockDataAt(sx, sy, itr_sz, WOOL_BLACK)

            sy += 1

            level.setBlockAt(sx, sy, sz, TORCH)
            level.setBlockDataAt(sx, sy, sz, TORCH_ON_GROUND)

            sz -= 1

            level.setBlockAt(sx, sy, sz, REDSTONE)

            sz -= 1

            level.setBlockAt(sx, sy, sz, REPEATER)
            
            # If we are finished with the whole thing, make the lead the exposes
            # The signal to the rest of the world
            
            if termIndex == len(minterms) - 1:

                sz += 2
                sy += 1
                
                data = WOOL_BLACK if use_output_color_key == None else use_output_color_key[comb_equation.name]
                
                for iter_sz in range(sz, sz+7, 1):
                    level.setBlockAt(sx, sy, iter_sz, WOOL)
                    level.setBlockDataAt(sx, sy, iter_sz, data)
                    sy += 1
                    level.setBlockAt(sx, sy, iter_sz, REDSTONE)
                    sy -= 1
                
                sz += 7
                
                level.setBlockAt(sx, sy, sz, WOOL)
                level.setBlockDataAt(sx, sy, sz, data)
                
                sy += 1
                
                level.setBlockAt(sx, sy, sz, REPEATER)
                level.setBlockDataAt(sx, sy, sz, REPEATER_TOWARD_POS_Z)
                
                lead_location = [sx, sy, sz]
                
                

            # -----------------------------------------------------

            sx = box.width - 1
            sy = currentFarTowerTopY
            sz = currentFarTowerTopZ

            sz -= 1

            level.setBlockAt(sx, sy, sz, WOOL)
            level.setBlockDataAt(sx, sy, sz, WOOL_BLACK)

            sy += 1

            level.setBlockAt(sx, sy, sz, 75)
            level.setBlockDataAt(sx, sy, sz, 5)

            sz += 1

            level.setBlockAt(sx, sy, sz, WOOL)
            level.setBlockDataAt(sx, sy, sz, WOOL_BLACK)

            sz -= 1
            sy += 1

            level.setBlockAt(sx, sy, sz, WOOL)
            level.setBlockDataAt(sx, sy, sz, WOOL_BLACK)

            sz += 1

            level.setBlockAt(sx, sy, sz, REDSTONE)

            sz += 1

            level.setBlockAt(sx, sy, sz, WOOL)
            level.setBlockDataAt(sx, sy, sz, WOOL_BLACK)

            sy += 1

            level.setBlockAt(sx, sy, sz, TORCH)
            level.setBlockDataAt(sx, sy, sz, TORCH_ON_GROUND)
                
                    
            
            # Now reset the variables for working up the next paste:

            cy += 4
            numTerms = 0
            side = CLOSE_SIDE
            cz = 1

        else:

            cy += 1


#    level.setBlockAt(0, 0, 0, 20)
#    level.setBlockAt(box.width-1, box.height-1, box.length-1, 20)
    
#    # Flip the entire schematic around to help make the fitting routine more 'sane'
#    # Also adjust location variables (like the locations of the lead and inputs) to
#    # reflect the Z-flip
#    
#    level.flipEastWest()
#    lead_location[2] = sizeZ - 1 - lead_location[2]
#    for ril in relative_input_locations.values():
#        ril[2] = sizeZ - 1 - ril[2]
    
#    level.setBlockAt(*lead_location, blockID = 35)
#    level.setBlockDataAt(*lead_location, newdata = 0)
#    
#    for ril in relative_input_locations.values():
#        level.setBlockAt(*ril, blockID = GLASS)
    
    ret = CombinationalElement(level)
    ret.relative_output_locations = {comb_equation.name : lead_location}
    ret.relative_input_locations = relative_input_locations
    ret.size = (sizeX, sizeY, sizeZ)
    
    return ret
    
    