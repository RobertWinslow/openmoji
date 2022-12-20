# -*- coding: utf-8 -*-
'''
To Use:
1. Adjust the global parameters in the first section below.
2. type `fontforge -script build_black_font_with_fontforge.py` in the terminal.

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
import csv
import os

INPUTFOLDER = '../black/svg'
OUTPUTFILENAME = '../font/OpenMoji-Black.ttf'
PLACEHOLDERGEOMETRYSVG = '../black/svg/25A1.svg'
DATACSV = '../data/openmoji.csv' #Used for skintones and alt hexcodes. Openmoji specific. 

font = fontforge.font()
font.familyname = "OpenMoji Black"
font.fullname = "OpenMoji Black"
font.copyright = "All emojis designed by OpenMoji - the open-source emoji and icon project. License: CC BY-SA 4.0"
font.version = "14.0"

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
# If the following parameter is set to a positive integer, a blank 'space' character is included in the font.
SPACEWIDTH = MONOSPACEWIDTH

# Many glyphs have an emoji and a non-emoji presentation
# If this is set to False, there may be inconsistent rendering across applications.
# (Sadly, some applications will render the system-default-emoji when FE0F is present, 
#   even if the font explicitly contains an FE0F in the ligature.)
INCLUDEALTERNATEHEXCODES = True
# In a monochrome font, skin tone variations look the same.
# If set to False, only the base version of each glyph will be added to the font,
#   and the skintone variants will render as sequences of glyphs (recommended True)
INCLUDESKINTONEVARIANTS = True
# In a monochrome font, the country flags are just blank rectangles.
# If this is set to False, then the flags will be rendered as sequences of indicator codes.
INCLUDECOUNTRYFLAGS = False








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
codetuples = [(tuple(filename[:-4].split('-')), filename) for filename in files if filename.endswith('.svg')]

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
# And use the DATACSV to associate each skintone variant with its base form.
# The DATACSV is also used to indentify flag characters and optionall exclude them.
skintoneMap = dict()
flagSet = set()
with open(DATACSV,'r',encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['skintone'] != '':
            codepoints = tuple(row['hexcode'].split('-'))
            base_name = 'u'+row['skintone_base_hexcode'].replace('-','_u')
            skintoneMap[codepoints] = base_name
        if row['subgroups'] in ['country-flag', ]: # 'subdivision-flag','flag','flags' might also reasonably be included in this list.
            codepoints = tuple(row['hexcode'].split('-'))
            flagSet.add(codepoints)

combocharacters = [(codepoints,filename) for codepoints,filename in codetuples if len(codepoints)>1]
if INCLUDECOUNTRYFLAGS == False:
    combocharacters = [(codepoints,filename) for codepoints,filename in combocharacters if codepoints not in flagSet]
skintonevariants = [(codepoints,filename) for codepoints,filename in combocharacters if codepoints in skintoneMap]
othercombos = [(codepoints,filename) for codepoints,filename in combocharacters if codepoints not in skintoneMap]

# Imports glyphs for all the non-skintone combination characters. 
for codepoints,filename in othercombos:
    components = tuple('u'+codepoint for codepoint in codepoints)
    char = font.createChar(-1, '_'.join(components))
    char.addPosSub("mySubtable", components)
    importAndCleanOutlines(INPUTFOLDER+'/'+filename,char)
    # Also add a ligature which excludes the FE0F selector(s)
    if len(codepoints) > 2 and INCLUDEALTERNATEHEXCODES:
        nonFE0Fcomponents = tuple('u'+codepoint for codepoint in codepoints if codepoint != 'FE0F')
        if components != nonFE0Fcomponents:
            char.addPosSub("mySubtable", nonFE0Fcomponents)


# Handle the skintone variants last so that we can reference the other glyphs instead of importing redundant outlines.
# The following links each skintone variant character to its "base" counterpart with no skin tones.
if INCLUDESKINTONEVARIANTS:
    for codepoints,filename in skintonevariants:
        components = tuple('u'+codepoint for codepoint in codepoints)
        char = font.createMappedChar(skintoneMap[codepoints]) #FF's create... functions return the glyph if it already exists.
        char.addPosSub("mySubtable", components)
        # Also add a ligature which excludes the FE0F selector(s)
        if len(codepoints) > 2 and INCLUDEALTERNATEHEXCODES:
            nonFE0Fcomponents = tuple('u'+codepoint for codepoint in codepoints if codepoint != 'FE0F')
            if components != nonFE0Fcomponents:
                char.addPosSub("mySubtable", nonFE0Fcomponents)


# Include ligatures for alternate hexcodes.
# The current algorithm iteration takes advantage of the fact that 
# the first column of 'openmoji.csv' uses the 'fully-qualified' glyph
# while the filename and hexcode entries use the abbreviated version
# (No such multiple-presentation characters have been added since emoji v2.0,
#   so it might be sensible to hardcode the list into the file.)
def padCodepoint(codepoint):
    # This function just sloppily deals with an annoying edgecase
    # When glyph contain digits as codepoints, there are leading zeros in the file names.
    if len(codepoint) == 2:
        return '00'+codepoint
    else:
        return codepoint
if INCLUDEALTERNATEHEXCODES:
    with open(DATACSV,'r',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Compare the codepoints of the emoji to its listed hex code...
            newCodepoints  = tuple(hex(ord(c))[2:].upper() for c in row['emoji']) #convert glyph to hexcode tuple
            newCodepoints = tuple(padCodepoint(codepoint) for codepoint in newCodepoints)
            existingCodepoints = tuple(row['hexcode'].split('-'))
            if newCodepoints != existingCodepoints:
                # ... and create a ligature if they don't match up.
                print("Adding alternate codepoint for ",row['emoji'], newCodepoints)
                existingName = 'u'+'_u'.join(existingCodepoints)
                newComponents = tuple('u'+codepoint for codepoint in newCodepoints)
                char = font.createMappedChar(existingName) #FF's create... functions return the glyph if it already exists.
                char.addPosSub("mySubtable", newComponents)








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


# If the parameter is positive, include a blank glyph for 'space'.
# For a glyph without geometry to be included in the font, FF requires its width to be manually set.
# As such, this step must be done after everything else.
if SPACEWIDTH:
    spaceChar = font.createChar(32, 'u0020')
    spaceChar.width = SPACEWIDTH







#%% FINALLY - Generate the font
print("Generating black font to", OUTPUTFILENAME)
font.generate(OUTPUTFILENAME)








