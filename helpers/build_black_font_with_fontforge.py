# -*- coding: utf-8 -*-
'''
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

INPUTFOLDER = '../black/svg'
OUTPUTFILENAME = '../font/OpenMoji-Black.ttf'
PLACEHOLDERGEOMETRYSVG = '../black/svg/25A1.svg'

font = fontforge.font()
font.familyname = "OpenMoji"
font.fullname = "OpenMoji Black Regular"
font.copyright = "All emojis designed by OpenMoji - the open-source emoji and icon project. License: CC BY-SA 4.0"
font.version = "13.1.1"

# The following variables are for scaling the imported outlines.
SVGHEIGHT = 72 # units of height of source svg viewbox. 
GLYPHHEIGHT = 1300 # font units, default = 1000
PORTIONABOVEBASELINE = 0.8 # default is 0.8
# The following parameter sets the spacing between characters. 
# It is made redundant by MONOSPACEWIDTH if that parameter is set.
SEPARATION = 0
# If the following parameter is set to a positive integer, all characters are set to that width.
# Set it to 0 or None to make the font non-monospaced.
MONOSPACEWIDTH = GLYPHHEIGHT
# If the following parameter is set to a positive integer, all characters wider than this are scaled down.
# Set it to 0 or None to allow characters to be extra wide.
# If MAXWIDTH is unset, but MONOSPACEWIDTH is set, then some glyphs may have contours outside of their bounding box.
MAXWIDTH = MONOSPACEWIDTH









#%% SECTION TWO A - Define function for importing outlines.

def importAndCleanOutlines(outlinefile,glyph):
    #print(outlinefile)
    glyph.importOutlines(outlinefile, simplify=True, correctdir=False, accuracy=0.25, scale=False)
    glyph.removeOverlap()
    SCALEFACTOR = GLYPHHEIGHT/SVGHEIGHT
    foregroundlayer = glyph.foreground
    for contour in foregroundlayer:
        for point in contour:
            point.transform((1,0,0,1,0,-800)) # Translate top of glyph down to baseline.
            point.transform((SCALEFACTOR,0,0,SCALEFACTOR,0,0)) # Scale up. Top of glyph will remain at baseline. 
            point.transform((1,0,0,1,0,PORTIONABOVEBASELINE*GLYPHHEIGHT)) # translate up to desired cap height
    glyph.setLayer(foregroundlayer,'Fore')

#%% SECTION TWO B - CREATE GLYPHS FROM THE SVG SOURCE FILES
# Scan the directory of SVG files and make a list of files and codepoints to process
files = os.listdir(INPUTFOLDER)
codetuples = [(filename[:-4].split('-'), filename) for filename in files if filename.endswith('.svg')]

# Start by loading up all the single codepoint characters.
simplecharacters = [(codepoints[0],filename) for codepoints,filename in codetuples if len(codepoints)==1]
for codepoint, filename in simplecharacters:
    char = font.createChar(int(codepoint,16), 'u'+codepoint)
    importAndCleanOutlines(INPUTFOLDER+'/'+filename,char)

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
    importAndCleanOutlines(PLACEHOLDERGEOMETRYSVG,char)

# Now make the combination characters via FontForge's ligature feature.
# To be quite honest, I don't fully understand what all this syntax up front is doing.
# Just treat these next couple of lines as if they are a mystical incantation.
font.addLookup('myLookup','gsub_ligature',None,(("liga",(('DFLT',("dflt")),)),))
font.addLookupSubtable("myLookup", "mySubtable")

# Split the skintone variants from all of the other combination characters
SKINTONECODEPOINTS = ['1F3FF','1F3FE','1F3FD','1F3FC','1F3FB','1f3ff','1f3fe','1f3fd','1f3fc','1f3fb',]
isSkintoneVariant  = lambda components : any(skintone in components for skintone in SKINTONECODEPOINTS)

combocharacters = [(codepoints,filename) for codepoints,filename in codetuples if len(codepoints)>1]
skintonevariants = [(codepoints,filename) for codepoints,filename in combocharacters if isSkintoneVariant(codepoints)]
othercombos = [(codepoints,filename) for codepoints,filename in combocharacters if not isSkintoneVariant(codepoints)]

# Imports glyphs for all the non-skintone combination characters. 
for codepoints,filename in othercombos:
    components = tuple('u'+codepoint for codepoint in codepoints)
    char = font.createChar(-1, '_'.join(components))
    char.addPosSub("mySubtable", components)
    importAndCleanOutlines(INPUTFOLDER+'/'+filename,char)

# Handle the skintone variants last so that we can reference the other glyphs instead of importing redundant outlines.
# The following links each skintone variant character to its "basic" counterpart with no skin tones.
# There are some skintone variants that need to be manually coded in because there isn't an underlying basic version
# And some skintone variants have the skintone selector replacing an emoji selector FE0F.
skintone_specialcases = {
    'u1F469_u200D_u1F91D_u200D_u1F468':'u1F46B', # woman holding hands with man
    'u1F468_u200D_u1F91D_u200D_u1F468':'u1F46C', # men holding hands
    'u1F469_u200D_u1F91D_u200D_u1F469':'u1F46D', # women holding hands
    'u1F9D1_u200D_u2764_uFE0F_u200D_u1F48B_u200D_u1F9D1':'u1F48F', # two people kissing
    'u1F9D1_u200D_u2764_uFE0F_u200D_u1F9D1':'u1F491', # couple with heart
    'u1FAF1_u200D_u1FAF2':'u1F91D', # handshake halves -> handshake
    }

for codepoints,filename in skintonevariants:
    components = tuple('u'+codepoint for codepoint in codepoints)
    basicname = '_'.join(['u'+codepoint for codepoint in codepoints if codepoint not in SKINTONECODEPOINTS])
    if font.findEncodingSlot(basicname) != -1: # This means that the basic version of the glyph exists.
        continue
    elif basicname in skintone_specialcases: # This means the skintone variants use different codepoints than their basic counterpart
        basicname = skintone_specialcases[basicname]
    else: # And otherwise, I'm assuming that the problem lies in the variation selector missing from skintone variant version.
        basicname = '_'.join(components)
        for skintone in SKINTONECODEPOINTS:
            basicname = basicname.replace(skintone,'FE0F')
    
    # The final step is wrapped in a conditional for the sake of assisting future debugging/updates.
    # Unfortunately, skintone variants are implemented somewhat inconsistently in the emoji standards.
    # If a new special case is introduced, it won't *break* the font; It will just result in a duplicate glyph.
    if font.findEncodingSlot(basicname) != -1:
        char = font.createMappedChar(basicname) #FF's create... functions return the glyph if it already exists.
        char.addPosSub("mySubtable", components)
    else:
        print("This is a skintone variant, but I can't find a non-skintoned version:")
        print(' '.join(codepoints))
        print("Please check whether a new case needs to be added to skintone_specialcases in build_black_font_with_fontforge.py")
        #print(basicname)
        char = font.createChar(-1, '_'.join(components))
        char.addPosSub("mySubtable", components)
        importAndCleanOutlines(INPUTFOLDER+'/'+filename,char)









#%% SECTION THREE - Adjust some of the font's global properties.
# Automagically adjust the horizontal position of the font.
font.selection.all()
font.autoWidth(SEPARATION)

#%% If the parameter is set, scale down the very wide glyphs
# This can make the unusually wide glyphs overlap a bit.
if MAXWIDTH:
    for g in font.glyphs():
        if g.width > MAXWIDTH:
            print(g)
            rescalefactor = MAXWIDTH / g.width
            g.transform((rescalefactor,0,0,rescalefactor,0,0))

font.selection.all()
font.autoWidth(SEPARATION)

# If the parameter is set, standardize the spacing to the right and left
# This can make the unusually wide glyphs overlap a bit.
if MONOSPACEWIDTH:
    for g in font.glyphs():
        bearing = int((MONOSPACEWIDTH-g.width)/2)
        g.left_side_bearing = bearing
        g.right_side_bearing = bearing









#%% FINALLY - Generate the font
print("Generating black font to", OUTPUTFILENAME)
font.generate(OUTPUTFILENAME)








