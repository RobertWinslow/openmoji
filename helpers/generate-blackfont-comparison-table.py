'''
This script scrapes the openmoji data file, and uses it to create an html table 
for the sake of comparing the black fonts to the png versions of each glyph.
The resulting html file can be found in the fonts folder, 
and can be viewed in any internet browser.
'''



#%% IMPORTS AND PARAMETERS
import csv

DATAFILE = '../data/openmoji.csv'
IMGFOLDER = '../black/72x72/'
IMGTYPE = "PNG" 

OUTPUTFILE = '../font/black-font-comparison-table.html'

NANOEMOJIFONT = 'OpenMoji-Black.ttf'
FONTFORGEFONT = 'OpenMoji-Black-FontForge.ttf'




# %% SCRAPE THE DATA FILE TO BUILD A LIST OF (NON-SKINTONE-VARIANT) EMOJIS

emojilist = []
with open(DATAFILE, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row['skintone_base_emoji'] == '':
            emojilist.append(row)




# %% USE THIS LABEL TO CREATE THE BODY CONTENT OF THE HTML DOCUMENT

def createTableRow(emoji):
    cell0 = f"{emoji['hexcode']}<br><small>{emoji['annotation']}</small><br>{emoji['emoji']}"
    cell1 = f"<img src='{IMGFOLDER+emoji['hexcode']}.{IMGTYPE}'/>"
    cell2 = emoji['emoji']
    cell3 = emoji['emoji']
    rowtext = f"<tr><td>{cell0}</td><td>{cell1}</td><td>{cell2}</td><td>{cell3}</td></tr>\n"
    return rowtext

TABLEPREFIX = "<table>\n<thead><tr><th></th><th>PNG</th><th>NanoEmoji</th><th>FontForge</th></tr></thead>\n<tbody>\n"
TABLESUFFIX = "</tbody>\n</table>\n\n\n"

previousGroup = None
previousSubgroup = None

bodyString = ""
for emoji in emojilist:
    # If need be, end the table, and start a new table after an appropriate header.
    group, subgroup = emoji['group'], emoji['subgroups']
    if (previousGroup != group or previousSubgroup != subgroup) and previousGroup != None:
        bodyString += TABLESUFFIX
    if previousGroup != group:
        bodyString += f"<h2>{group}</h2>\n"
    if previousSubgroup != subgroup:
        bodyString += f"<h3>{subgroup}</h2>\n"
    if previousGroup != group or previousSubgroup != subgroup:
        bodyString += TABLEPREFIX
    previousGroup, previousSubgroup = group, subgroup
    # Regardless, add a table row for the emoji 
    bodyString += createTableRow(emoji)
bodyString += TABLESUFFIX



# %% WRAP THE BODY CONTENT WIH STYLE ETC, AND OUTPUT TO HTML

STYLESTRING = '''
<style>
table, th, td {
    border: 1px solid #ccc;
}

td {
    vertical-align: middle;
    text-align: center;
}

@font-face {
  font-family: 'NanoEmoji Black Font';
  src: url(NEPLACEHOLDER);
}
td:nth-child(3) {
  font-family: 'NanoEmoji Black Font';
  font-size: 50px;
  padding: 0px;
}

@font-face {
  font-family: 'Fontforge Black Font';
  src: url(FFPLACEHOLDER);
}
td:nth-child(4) {
  font-family: 'Fontforge Black Font';
  font-size: 50px;
  padding: 0px;
}

</style>

'''.replace("NEPLACEHOLDER",NANOEMOJIFONT).replace("FFPLACEHOLDER", FONTFORGEFONT)

with open(OUTPUTFILE, 'w') as f:
    f.write("<html><head>")
    f.write(STYLESTRING)
    f.write("</head><body>\n<h1>Comparison of Rendered Black Glyphs</h1>\n\n\n")
    f.write(bodyString)
    f.write("</body></html>")




# %%
