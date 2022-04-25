# encoding: utf-8

# This File generates a html file which can be used to view every glyph.
# Glyphs are shown based on both color and black svg sources, 
# as well as from color and black font files.
# I created this file to check for problems in the openmoji black font contours.
# Unfortunately, some of the issues are too idiosyncratic to identify via script.
# Hence the need to scroll past glyphs looking for mismatches.
# Some sort of automated image analysis might work. But I'm not looking for perfection; just 'good enough'.




#%% Step 1. Read in the information about the glyphs and fonts from other files in the openmoji directories.

emojilist = []
with open('../data/openmoji.csv', 'r', encoding='utf8') as f:
    for line in f.readlines()[1:]:
        linedata = line.split(',')
        glyph,codepoint,name,subgroup = linedata[0],linedata[1],linedata[4],linedata[3]
        emojilist.append((glyph,codepoint,name,subgroup))

#with open('openmoji.css', 'r') as f:
#    emojifontstyle = f.read()





#%% Step 2. Define the snippets which will be used to build the html.

def makeGlyphRowSnippet(glyph,codepoint,name):
    snippet  = '<tr>'
    snippet += f'<td>{glyph}<br>{codepoint}<br><small>{name}</small></td>'
    snippet += f'<td><img src = "../black/svg/{codepoint}.svg"></td>'
    snippet += f'<td>{glyph}</td>'
    snippet += f'<td><img src = "../color/svg/{codepoint}.svg"></td>'
    snippet += f'<td>{glyph}</td>'
    snippet += '</tr>'+'\n'
    return snippet

htmlprefixsnippet = '''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Openmoji Font Comparison</title>
<style>
@font-face {
    font-family: "OpenMojiColor";
    src: url("OpenMoji-Color.ttf") format("truetype");
    font-style: Color;
}
@font-face {
    font-family: "OpenMojiBlack";
    src: url("OpenMoji-Black.ttf") format("truetype");
    font-style: Black;
}
img {
    width: 65px;
}
table, th, td {
border: 1px solid;
    text-align: center;
}
td:nth-child(3) {
    font-family: "OpenMojiBlack";
    font-size: 50px;
}
td:nth-child(5) {
    font-family: "OpenMojiColor";
    font-size: 50px;
}
</style>
</head>

<body>
<table>
<thead><th></th><th>Black SVG</th><th>Black Font</th><th>Color SVG</th><th>Color Font</th></thead>
'''

htmlsuffixsnippet = '</table></body></html>'

pretablesnippet = '''<table>
<thead><th></th><th>Black SVG</th><th>Black Font</th><th>Color SVG</th><th>Color Font</th></thead>
'''

posttablesnippet = '</table>'


#%% Step 3. Assemble the html file for viewing all the glyphs
# The resulting html file may take a while to load in a browser.


with open('allGlyphsComparison.html', 'w', encoding='utf8') as f:
    f.write(htmlprefixsnippet)
    currentsubgroup = 'face-smiling' # This is the first subgroup
    for glyph,codepoint,name,subgroup in emojilist:
        if subgroup != currentsubgroup: # Start a new table when we switch subgroups.
            f.write(posttablesnippet)
            f.write(f'<h3>{subgroup}</h3>')
            f.write(pretablesnippet)
            currentsubgroup = subgroup
        glyphRowSnippet = f'test {glyph}'
        f.write(makeGlyphRowSnippet(glyph,codepoint,name))
    f.write(htmlsuffixsnippet)


# %%
