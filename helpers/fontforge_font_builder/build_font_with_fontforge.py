# -*- coding: utf-8 -*-
'''
Author:
Robert Winslow

To Use:
1. Adjust the global parameters in the first section below.
2. type `fontforge -script build_font_with_fontforge.py` in the terminal.

Description:
This script uses FontForge to build a very basic monochrome font from a folder of SVG files.
Each SVG file must be named with the codepoint of the unicode character it is to be mapped to. 
    EG `1F94B.svg`
If a glyph maps to a sequence of codepoints, seperate the codepoints with `-` in the SVG file's name.
    EG `1F468-200D-1F9B3.svg`
If there are codepoints which are part of a sequence but lack their own SVG, then placeholder geometry is used.

See here for documentation about FontForge's scripting library:
https://fontforge.org/docs/scripting/python/fontforge.html
'''






#%% SECTION ONE - Imports and parameters
import fontforge
import os

INPUTFOLDER = '../../black/svg'
OUTPUTFILENAME = '../../font/OpenMoji-MonoChrome.ttf'
PLACEHOLDERGEOMETRYSVG = 'placeholder.svg'

font = fontforge.font()
font.familyname = "OpenMoji"
font.fontname = "OpenMoji Monochrome"
font.fullname = "OpenMoji Monochrome Regular"
font.copyright = "All emojis designed by OpenMoji - the open-source emoji and icon project. License: CC BY-SA 4.0"
font.version = "v0.7 e13.1"

# The following parameter sets the spacing between characters. 
# It is made redundant by MONOSPACEWIDTH if that parameter is set.
SEPARATION = 0
# If the following parameter is set to a positive integer, all characters are set to that width.
# Set it to 0 or None to make the font non-monospaced.
MONOSPACEWIDTH = None









#%% SECTION TWO - CREATE GLYPHS FROM THE SVG SOURCE FILES
# Scan the directory of SVG files and make a list of files and codepoints to process
files = os.listdir(INPUTFOLDER)
codetuples = [(filename[:-4].split('-'), filename) for filename in files if filename.endswith('.svg')]

# Start by loading up all the single codepoint characters.
simplecharacters = [(codepoints[0],filename) for codepoints,filename in codetuples if len(codepoints)==1]
for codepoint, filename in simplecharacters:
    print(filename)
    char = font.createChar(int(codepoint,16), 'u'+codepoint)
    char.importOutlines(INPUTFOLDER+'/'+filename, simplify=True, correctdir=False, accuracy=2)
    char.removeOverlap()

# Manually add 200D (ZWJ), FE0F, and other individual codepoints as glyphs as needed.
# If a codepoint is not present as a glyph, we can't add it into a combined character.
# And if geometry isn't added to a glyph, FontForge will discard it.
# Therefore a placeholder glyph is used.
presentcomponents = set([g.glyphname for g in font.glyphs()])
missingcodepoints = set()
for codepoints,filename in codetuples:
    for codepoint in codepoints:
        if 'u'+codepoint not in presentcomponents:
            missingcodepoints.add(codepoint)
for codepoint in missingcodepoints:
    char = font.createChar(int(codepoint,16), 'u'+codepoint)
    char.importOutlines(PLACEHOLDERGEOMETRYSVG)

# Now make the combination characters via FontForge's ligature feature.
# To be quite honest, I don't fully understand what all this syntax up front is doing.
# Just treat these next couple of lines as if they are a mystical incantation.
font.addLookup('myLookup','gsub_ligature',None,(("liga",(('DFLT',("dflt")),)),))
font.addLookupSubtable("myLookup", "mySubtable")
combocharacters = [(codepoints,filename) for codepoints,filename in codetuples if len(codepoints)>1]
for codepoints,filename in combocharacters:
    print(filename)
    components = tuple('u'+codepoint for codepoint in codepoints)
    char = font.createChar(-1, '_'.join(components))
    char.addPosSub("mySubtable", components)
    char.importOutlines(INPUTFOLDER+'/'+filename, simplify=True, correctdir=False, accuracy=2)
    char.removeOverlap()







#%% SECTION THREE - Adjust some of the font's properties.
# Automagically adjust the horizontal position of the font.
font.selection.all()
font.autoWidth(SEPARATION)

# Adjust the size of the font.
# Default em size is 1000 units, but that makes the font look too small.
# Changing to 800 units makes the font look similar size to the canonical OpenMoji-Black.ttf
font.ascent = 750
font.descent = 0
font.em = font.ascent + font.descent

#%% If the parameter is set, standardize the spacing to the right and left
# This will sadly make the unusually wide glyphs overlap a bit.
if MONOSPACEWIDTH:
    print('-----------------')
    for g in font.glyphs():
        bearing = int((MONOSPACEWIDTH-g.width)/2)
        g.left_side_bearing = bearing
        g.right_side_bearing = bearing








#%% FINALLY - Generate the font
font.generate(OUTPUTFILENAME)






