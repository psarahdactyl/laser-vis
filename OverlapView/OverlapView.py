#adapted from https://www.cairographics.org/cookbook/svgtopycairo/
import cairocffi as cairo
from pyparsing import *
import os, sys
import xml.etree.ElementTree as et
import svgpathtools as sp

#get file
file = sys.argv[1]
pathlist, attlist, svgatt = sp.svg2paths2(file)
sp.wsvg(pathlist, attributes = attlist, filename = file)
xml_file = os.path.abspath(__file__)
xml_file = os.path.dirname(xml_file)
xml_file = os.path.join(xml_file, file)

def get_commands(xml_file):
    #parsing commands
    dot = Literal(".")
    comma = Literal(",").suppress()
    floater = Combine(Optional("-") + Word(nums) + dot + Word(nums))
    couple = floater + comma + floater
    M_command = "M" + Group(couple)
    C_command = "C" + Group(couple + couple + couple)
    L_command = "L" + Group(couple)
    Z_command = "Z"
    svgcommand = M_command | C_command | L_command | Z_command
    phrase = OneOrMore(Group(svgcommand))

    #parse using pyparsing
    tree = et.parse(xml_file)
    ns = "http://www.w3.org/2000/svg" #The XML namespace.
    root = tree.getroot()
    rval2 = [root.get("viewBox"), root.get('width'), root.get('height')]
    paths = []
    for group in tree.iter('{%s}svg' % ns):
        for e in group.iter('{%s}path' % ns):
            p = e.get("d")
            tokens = phrase.parseString(p.upper())
            paths.append(tokens) # paths is a global var.

    cairo_commands = ""
    command_list = []
    for tokens in paths:
        for command,couples in tokens: #looks weird, but it works :)
            c = couples.asList()
            #c[:] = [str(float(i)*10.0) for i in c]
            if command == "M":
                cairo_commands += "ctx.move_to(%s,%s);" % (c[0],c[1])
            if command == "C":
                cairo_commands += "ctx.curve_to(%s,%s,%s,%s,%s,%s);" % (c[0],c[1],c[2],c[3],c[4],c[5])
            if command == "L":
                cairo_commands += "ctx.line_to(%s,%s);" % (c[0],c[1])
            if command == "Z":
                cairo_commands += "ctx.close_path();"

        command_list.append(cairo_commands) #Add them to the list
        cairo_commands = ""

    return command_list, rval2

command_list, attrib = get_commands(xml_file)
def renderThis(command_list, attrib):
    
    accum = ''
    for i in range(len(attrib[1])):
        if attrib[1][i] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            accum += attrib[1][i]
    width = int(accum)
    accum = ''
    for i in range(len(attrib[2])):
        if attrib[2][i] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            accum += attrib[2][i]
    height = int(accum)

    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(img)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.set_line_width(10.0)
    ctx.set_source_rgba(1.0, 1.0, 1.0, 0.25)
    ctx.paint()
    
    ctx.set_source_rgba(0.05,0.04,0.03, 1.0)
    ctx.set_operator(cairo.OPERATOR_ADD)
    for c in command_list:
        exec(c)
        ctx.stroke()
    img.write_to_png("output.png")
    return True

renderThis(command_list, attrib)


