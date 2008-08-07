from __future__ import with_statement

import re
from OpenVG.constants import *
from OpenVG import VG


color_table = dict(aliceblue=(240, 248, 255),
                   antiquewhite=(250, 235, 215),
                   aqua=(0, 255, 255),
                   aquamarine=(127, 255, 212),
                   azure=(240, 255, 255),
                   beige=(245, 245, 220),
                   bisque=(255, 228, 196),
                   black=(0, 0, 0),
                   blanchedalmond=(255, 235, 205),
                   blue=(0, 0, 255),
                   blueviolet=(138, 43, 226),
                   brown=(165, 42, 42),
                   burlywood=(222, 184, 135),
                   cadetblue=(95, 158, 160),
                   chartreuse=(127, 255, 0),
                   chocolate=(210, 105, 30),
                   coral=(255, 127, 80),
                   cornflowerblue=(100, 149, 237),
                   cornsilk=(255, 248, 220),
                   crimson=(220, 20, 60),
                   cyan=(0, 255, 255),
                   darkblue=(0, 0, 139),
                   darkcyan=(0, 139, 139),
                   darkgoldenrod=(184, 134, 11),
                   darkgray=(169, 169, 169),
                   darkgreen=(0, 100, 0),
                   darkgrey=(169, 169, 169),
                   darkkhaki=(189, 183, 107),
                   darkmagenta=(139, 0, 139),
                   darkolivegreen=(85, 107, 47),
                   darkorange=(255, 140, 0),
                   darkorchid=(153, 50, 204),
                   darkred=(139, 0, 0),
                   darksalmon=(233, 150, 122),
                   darkseagreen=(143, 188, 143),
                   darkslateblue=(72, 61, 139),
                   darkslategray=(47, 79, 79),
                   darkslategrey=(47, 79, 79),
                   darkturquoise=(0, 206, 209),
                   darkviolet=(148, 0, 211),
                   deeppink=(255, 20, 147),
                   deepskyblue=(0, 191, 255),
                   dimgray=(105, 105, 105),
                   dimgrey=(105, 105, 105),
                   dodgerblue=(30, 144, 255),
                   firebrick=(178, 34, 34),
                   floralwhite=(255, 250, 240),
                   forestgreen=(34, 139, 34),
                   fuchsia=(255, 0, 255),
                   gainsboro=(220, 220, 220),
                   ghostwhite=(248, 248, 255),
                   gold=(255, 215, 0),
                   goldenrod=(218, 165, 32),
                   gray=(128, 128, 128),
                   grey=(128, 128, 128),
                   green=(0, 128, 0),
                   greenyellow=(173, 255, 47),
                   honeydew=(240, 255, 240),
                   hotpink=(255, 105, 180),
                   indianred=(205, 92, 92),
                   indigo=(75, 0, 130),
                   ivory=(255, 255, 240),
                   khaki=(240, 230, 140),
                   lavender=(230, 230, 250),
                   lavenderblush=(255, 240, 245),
                   lawngreen=(124, 252, 0),
                   lemonchiffon=(255, 250, 205),
                   lightblue=(173, 216, 230),
                   lightcoral=(240, 128, 128),
                   lightcyan=(224, 255, 255),
                   lightgoldenrodyellow=(250, 250, 210),
                   lightgray=(211, 211, 211),
                   lightgreen=(144, 238, 144),
                   lightgrey=(211, 211, 211))

command_table = dict(M=VG_MOVE_TO_ABS, m=VG_MOVE_TO_REL,
                     Z=VG_CLOSE_PATH, z=VG_CLOSE_PATH,
                     L=VG_LINE_TO_ABS, l=VG_LINE_TO_REL,
                     H=VG_HLINE_TO_ABS, h=VG_HLINE_TO_REL,
                     V=VG_VLINE_TO_ABS, v=VG_VLINE_TO_REL,
                     C=VG_CUBIC_TO_ABS, c=VG_CUBIC_TO_REL,
                     S=VG_SCUBIC_TO_ABS, s=VG_SCUBIC_TO_REL,
                     Q=VG_QUAD_TO_ABS, q=VG_QUAD_TO_REL,
                     T=VG_SQUAD_TO_ABS, t=VG_SQUAD_TO_REL)
#No arc support yet. More parsing annoyancese

class Group(object):
    def __init__(self, children, style, paint_mode, transform=None):
        self.children = children
        self.style = style
        self.paint_mode = paint_mode
        self.transform = transform

    def draw(self):
        with self.style:
            for child in self.children:
                if isinstance(child, Group):
                    child.draw()
                elif child.style:
                    with child.style:
                        child.draw(self.paint_mode)
                else:
                    child.draw(self.paint_mode)
        

def arg_count(command):
    takes_one = (VG_HLINE_TO, VG_VLINE_TO)
    takes_two = (VG_MOVE_TO, VG_LINE_TO, VG_SQUAD_TO)
    takes_four = (VG_QUAD_TO, VG_SCUBIC_TO)
    takes_six = (VG_CUBIC_TO,)
    command -= command % 2
    if command == VG_CLOSE_PATH:
        return 0
    elif command in takes_one:
        return 1
    elif command in takes_two:
        return 2
    elif command in takes_four:
        return 4
    elif command in takes_six:
        return 6
    else:
        raise ValueError("Unsupported command type % r" % command)

path_pattern = re.compile(r"([MZLHVCSQTA])([^MZLHVCSQTA]+)", re.IGNORECASE)
def parse_path_string(data):
    segments = []
    for command, args in path_pattern.findall(data):
        command = command.strip()
        vg_command = command_table[command]
        coords = map(float, re.split(r"(?:,|\s+)", args.strip()))

        count = arg_count(vg_command)
        if len(coords) % count:
            raise ValueError("Incorrect number of arguments for command %s" % command)
        if vg_command - (vg_command % 2) == VG_MOVE_TO and count > 2:
            segments.append((vg_command, coords[:2]))
            count -= 2
            del coords[:2]
            vg_command = VG_LINE_TO | (vg_command & VG_RELATIVE)

        for i in xrange(len(coords)/count):
            segments.append((vg_command, coords[i*count:(i+1)*count]))
    return segments

def parse_color_string(data):
    data = data.strip()
    if data.startswith("rgb"):
        s = data[data.index("(") + 1:data.rindex(")")]
        r, g, b = map(int, s.split(","))
    elif data.startswith("#"):
        s = re.match(r"#\s*([0-9a-fA-F]{3,6})", data).group(1)
        if len(s) == 3:
            r = int(s[0]*2, 16)
            g = int(s[1]*2, 16)
            b = int(s[2]*2, 16)
        elif len(s) == 6:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
        else:
            raise ValueError("Hex colors must be 3 or 6 digits")
    elif data in color_table:
        r,g,b = color_table[data]
    else:
        raise ValueError("Invalid color '%s'" % data)

    return VG.ColorPaint((r/255.0, g/255.0, b/255.0, 1.0))

style_pattern = re.compile(r"(\w+)\s*:\s*([^;]+);")
def parse_style_string(data):
    do_fill = True
    do_stroke = True
    style = VG.Style()
    for name, value in style_pattern.findall(data):
        if name == "fill":
            if value == "none":
                do_fill = False
            else:
                style[VG_FILL_PATH] = parse_color_string(value)
        elif name == "stroke":
            if value == "none":
                do_stroke = False
            else:
                style[VG_STROKE_PATH] = parse_color_string(value)
        elif name == "stroke-width":
            style[VG_STROKE_LINE_WIDTH] = float(value)
        else:
            pass
    paint_mode = 0
    if do_stroke:
        paint_mode |= VG_FILL_PATH
    if do_fill:
        paint_mode |= VG_STROKE_PATH
    return style, paint_mode

transform_pattern = re.compile("(matrix|translate|scale|rotate|skewX|skewY)\s*\((.+?)\)")
def parse_transform_string(data):
    transforms = []
    def transform():
        for f, args in transforms:
            f(*args)
    for action, s in transform_pattern.findall(data):
        args = map(float, re.split(r"(?:,|\s+)", s))
        if action == "matrix":
            a, b, c, d, e, f = args
            M = (a, c, e, b, d, f, 0, 0, 1)
            transforms.append((VG.mult_matrix, (M,)))
        elif action == "translate":
            if len(args) < 2:
                args = args[0], 0.0
            transforms.append((VG.translate, args))
        elif action == "scale":
            if len(args) < 2:
                args = args[0], args[0]
            transforms.append((VG.scale, args))
        elif action == "rotate":
            if len(args) == 3:
                transforms.append((VG.translate, (args[1], args[2])))
                transforms.append((VG.rotate, (args[0],)))
                transforms.append((VG.translate, (-args[1], -args[2])))
            else:
                transforms.append((VG.rotate, (args[0],)))
        else:
            raise NotImplementedError
    return transform

def path_from_element(element):
    segments = parse_path_string(element.attrib["d"])
    if "style" in element.attrib:
        style, paint_mode = parse_style_string(element.attrib["style"])
    else:
        style = None

    p = VG.Path()
    p.style = style
    if segments:
        p.extend(segments)
    p.close()
    return p

def group_from_element(element):
    style, paint_mode = parse_style_string(element.get("style", ""))
    transform = parse_transform_string(element.get("transform", ""))
    children = []
    for i,child in enumerate(element):
        tag = child.tag[child.tag.rfind("}") + 1:]
        if tag == "g":
            children.append(group_from_element(child))
        elif tag == "path":
            children.append(path_from_element(child))
        else:
            raise NotImplementedError
    return Group(children, style, paint_mode, transform)
