'''
Gcode edits to make:

Determine height to make change
Insert filament change after external perimeter
Move internal fill on next layer to after perimeter


TODO:
- determine line for filament change (TYPE: External Perimeter) comment denotes it, see how prusaslicer filament change command is added. 
'''
import os

layer_height = int(input("Enter layer change for initial change (1 is one layer before change): "))
g_code_filepath = input("Enter gcode file path: ")
#g_code_filepath = "/Users/lawtonskaling/Documents/Stanford Junior Documents/ME 127/3D Print Two Color Engrave/Test Files/Simple Square Plain.gcode"

# Open file and read lines
with open(g_code_filepath, 'r') as file:
    g_code = file.readlines()

#layer_height = 0.2 #TODO: determine layer height

# Get list of all lines with layer change
layer_change_lines = [i for i, line in enumerate(g_code) if ";LAYER_CHANGE" in line]
#print(layer_change_lines)

# start of layer 2
layer_2_start = layer_change_lines[layer_height]
layer_2_end = layer_change_lines[layer_height + 1]

layer_2_gcode = g_code[layer_2_start:layer_2_end]

infill_start_lines = [
    i for i, line in enumerate(layer_2_gcode) 
    if any(infill_type in line for infill_type in [";TYPE:Solid infill", ";TYPE:Internal infill", ";TYPE:Bridge infill"])
]


if len(infill_start_lines) > 1:
    raise ValueError("More than one infill start line found, unable to edit file")

# Add pause before infill start - working!
infill_start_line = infill_start_lines[0] + layer_2_start 
g_code.insert(infill_start_line, "M600\n")
g_code.insert(infill_start_line, ";COLOR_CHANGE\n")


# Part 2: End of infill patch

# Find infill start line on 4th layer
layer_change_lines = [i for i, line in enumerate(g_code) if ";AFTER_LAYER_CHANGE" in line]
layer_4_start = layer_change_lines[layer_height + 1] + 1
layer_4_end = layer_change_lines[layer_height + 2]

layer_4_gcode = g_code[layer_4_start:layer_4_end]

infill_start_lines = [
    i for i, line in enumerate(layer_4_gcode) 
    if any(infill_type in line for infill_type in [";TYPE:Solid infill", ";TYPE:Internal infill", ";TYPE:Bridge infill"])
]


if len(infill_start_lines) > 1:
    raise ValueError("More than one infill start line found, unable to edit file")

infill_start_line = infill_start_lines[0] + layer_4_start

#find "; stop printing object" and set to infill_end_line
infill_end_lines = [i for i, line in enumerate(layer_4_gcode) if "; stop printing object" in line]

if len(infill_end_lines) > 1:
    raise ValueError("More than one infill end line found, unable to edit file")

infill_end_line = infill_end_lines[0] + layer_4_start

infill_lines = g_code[infill_start_line:infill_end_line]
#insert color change and pause at the end of the infill lines
infill_lines.insert(-1, ";COLOR_CHANGE\n")
infill_lines.insert(-1, "M600\n")

#remove infill lines from layer 4
g_code[infill_start_line:infill_end_line] = []

#insert infill lines at the start of layer 4
g_code[layer_4_start:layer_4_start] = infill_lines

# Write changes to file
with open(g_code_filepath, 'w') as file:
    file.writelines(g_code)

#update filename to [filename]_edited.gcode
new_g_code_filepath = g_code_filepath.replace(".gcode", "_edited.gcode")    
os.rename(g_code_filepath, new_g_code_filepath)

print("Gcode file edited successfully")
