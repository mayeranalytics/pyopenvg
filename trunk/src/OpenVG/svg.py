from math import cos, sin, tan
import re

import numpy

from OpenVG import VG
from OpenVG import VGU
##from OpenVG.font import Font
from OpenVG.constants import *

__all__ = ["SVGElement", "SVGContainer", "SVGPrimitive",
           "SVG", "Group",
           "Path", "Rect", "Ellipse", "Circle", "Line", "PolyLine", "Polygon",
           "SVG_PATH_COMMANDS", "SVG_COLORS", "SVG_TAG_MAP", "SVG_PIXELS_PER_UNIT",
           ]

class SVGElement(object):
    def __init__(self, style, paint_mode, transform):
        self.style = style
        self.paint_mode = paint_mode
        self.transform = transform
        
    def load_style_from_element(self, e):
        style = DeferredStyle.from_element(e)
        self.style = style
        self.paint_mode = style.paint_mode

    def load_transform_from_element(self, e):
        if "transform" in e.attrib:
            self.transform = to_matrix(e.attrib["transform"])
        else:
            self.transform = None

class SVGContainer(SVGElement):
    def __init__(self, children, style, paint_mode, transform):
        SVGElement.__init__(self, style, paint_mode, transform)
        self.children = children

    def draw(self):
        if self.transform:
            mat = VG.get_matrix()
            VG.mult_matrix(self.transform)

        if self.style:
            self.style.enable()

        for child in self.children:
            if isinstance(child, SVGContainer):
                child.draw()
            elif isinstance(child, SVGPrimitive):
                child.draw(self.paint_mode)

        if self.style:
            self.style.disable()
        
        if self.transform:
            VG.load_matrix(mat)

    def load_children_from_element(self, e):
        for child in e.getchildren():
            child_cls = SVG_TAG_MAP.get(child.tag[child.tag.rfind("}") + 1:], None)
            if child_cls:
                self.children.append(child_cls.from_element(child))

class SVGPrimitive(SVGElement):
    def __init__(self, style, paint_mode, transform):
        SVGElement.__init__(self, style, paint_mode, transform)
        self._path = None

    def draw(self, paint_mode=VG_STROKE_PATH):
        if self.paint_mode:
            paint_mode = self.paint_mode
        
        self.path.draw(paint_mode, style=self.style)

    def build_path(self):
        raise NotImplementedError

    def get_path(self):
        if self._path is not None:
            return self._path
        else:
            self._path = self.build_path()
            return self._path

    def set_path(self, value):
        self._path = value

    path = property(get_path, set_path)

class SVG(SVGContainer):
    def __init__(self, children, width, height, viewbox=None):
        SVGContainer.__init__(self, children, None, None, None)
        self.width = width
        self.height = height
        self.viewbox = viewbox
        self.transform = [1,  0,      0,
                          0, -1,      0,
                          0,  height, 1]

    @classmethod
    def from_element(cls, e):
        
        width = 0#to_px(e.attrib["width"])
        height = 0#to_px(e.attrib["height"])
        if "viewbox" in e.attrib:
            x,y, w,h = e.attrib["viewbox"].split()
            viewbox = ((to_px(x), to_px(y)), (to_px(w), to_px(h)))
        else:
            viewbox = None
        svg = cls([], width, height, viewbox)
        svg.load_children_from_element(e)

        return svg

class Group(SVGContainer):
    @classmethod
    def from_element(cls, e):
        g = cls([], None, None, None)
        g.load_style_from_element(e)
        g.load_transform_from_element(e)
        
        g.load_children_from_element(e)

        return g

path_pattern = re.compile(r"([MZLHVCSQTA])([^MZLHVCSQTA]+)", re.IGNORECASE)
class Path(SVGPrimitive):
    def __init__(self, data, style=None, paint_mode=None, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.data = data

    def build_path(self):
        path = VG.Path()
        path.extend(self.data)
        return path

    @classmethod
    def from_element(cls, e):
        segments = []
        for command, args in path_pattern.findall(e.attrib["d"]):
            command = command.strip()
            vg_command = SVG_PATH_COMMANDS[command]
            if vg_command == VG_CLOSE_PATH:
                segments.append((vg_command, ()))
                continue
            coords = map(to_number, re.split(r"(?:,|\s+)", args.strip()))

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

        path = cls(segments, None, None, None)
        path.load_style_from_element(e)
        path.load_transform_from_element(e)

        return path

class Rect(SVGPrimitive):
    def __init__(self, pos, width, height, rx=0, ry=0, style=None, paint_mode=None, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.position = pos
        self.width = width
        self.height = height
        self.rx = rx
        self.ry = ry

    def build_path(self):
        path = VG.Path()
        rx = self.rx
        ry = self.ry
        if rx == ry == 0:
            VGU.rect(path, self.position, (self.width, self.height))
        else:
            if rx > self.width/2.0:
                rx = self.width/2.0
            if ry > self.height/2.0:
                ry = self.height/2.0
            VGU.round_rect(path, self.position, (self.width, self.height), rx, ry)
        return path

class Ellipse(SVGPrimitive):
    def __init__(self, pos, rx, ry, style=None, paint_mode=None, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.position = pos
        self.rx = rx
        self.ry = ry

    def build_path(self):
        path = VG.Path()
        VGU.ellipse(path, self.position, (self.rx*2, self.ry*2))
        return path

class Circle(Ellipse):
    def __init__(self, pos, radius, style=None, paint_mode=None, transform=None):
        Ellipse.__init__(self, pos, radius, radius, style, paint_mode, transform)

    def get_radius(self):
        return self.rx

    def set_radius(self, value):
        self.rx = self.ry = value

    radius = property(get_radius, set_radius)

class Line(SVGPrimitive):
    def __init__(self, p1, p2, style=None, paint_mode=None, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.p1 = p1
        self.p2 = p2

    def build_path(self):
        path = VG.Path()
        VGU.line(path, self.p1, self.p2)
        return path

class PolyLine(SVGPrimitive):
    def __init__(self, points, closed=False, style=None, paint_mode=None, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.points = points
        self.closed = closed

    def build_path(self):
        path = VG.Path()
        VGU.polygon(path, self.points, self.closed)
        return path

class Polygon(PolyLine):
    def __init__(self, points, style=None, paint_mode=None, transform=None):
        PolyLine.__init__(self, points, True, style, paint_mode, transform)

style_pattern = re.compile(r"(\w+-?\w+)\s*:\s*([^;]+)(?:;|$)")
class DeferredStyle(VG.Style):
    def __init__(self, **kwargs):
        VG.Style.__init__(self, **kwargs)
        self.initialized = False
        self.paint_mode = VG_STROKE_PATH
        
    def enable(self):
        if not self.initialized:
            if self.fill_paint:
                const, args = self.fill_paint
                self.fill_paint = const(*args)
            if self.stroke_paint:
                const, args = self.stroke_paint
                self.stroke_paint = const(*args)
            self.initialized = True
        VG.Style.enable(self)

    @classmethod
    def from_element(cls, e):
        style = cls()
        
        do_fill = False
        do_stroke = False
        
        for name, value in style_pattern.findall(e.get("style","")) + e.attrib.items():
            name = name.lower().strip()
            value = value.lower().strip()
            if name == "fill":
                if value == "none":
                    do_fill = False
                else:
                    do_fill = True
                    style.fill_paint = (VG.ColorPaint, (to_rgb(value),))
            elif name == "stroke":
                if value == "none":
                    do_stroke = False
                else:
                    do_stroke = True
                    style.stroke_paint = (VG.ColorPaint, (to_rgb(value),))
            elif name == "stroke-width":
                style[VG_STROKE_LINE_WIDTH] = to_px(value)
            elif name == "stroke-linecap":
                if value == "round":
                    style[VG_STROKE_CAP_STYLE] = VG_CAP_ROUND
                elif value == "butt":
                    style[VG_STROKE_CAP_STYLE] = VG_CAP_BUTT
                elif value == "square":
                    style[VG_STROKE_CAP_STYLE] = VG_CAP_SQUARE
                else:
                    raise ValueError("Unknown stroke-linecap style \"%s\"" % value)
            elif name == "stroke-linejoin":
                if value == "round":
                    style[VG_STROKE_JOIN_STYLE] = VG_JOIN_ROUND
                elif value == "bevel":
                    style[VG_STROKE_JOIN_STYLE] = VG_JOIN_BEVEL
                elif value == "miter":
                    style[VG_STROKE_JOIN_STYLE] = VG_JOIN_MITER
                else:
                    raise ValueError("Unknown stroke-linejoin style \"%s\"" % value)
            elif name == "stroke-miterlimit":
                style[VG_STROKE_MITER_LIMIT] = to_px(value)
            elif name == "stroke-dashoffset":
                style[VG_STROKE_DASH_PHASE] = to_px(value)
            elif name == "stroke-dasharray":
                if value == "none":
                    style[VG_STROKE_DASH_PATTERN] = ()
                else:
                    style[VG_STROKE_DASH_PATTERN] = map(to_number, re.split(r"(\s*,\s*)|(?:\s*|,)", value))
            elif name == "fill-rule":
                if value == "evenodd":
                    style[VG_FILL_RULE] = VG_EVEN_ODD
                elif value == "nonzero":
                    style[VG_FILL_RULE] = VG_NON_ZERO

        paint_mode = 0
        if do_stroke:
            paint_mode |= VG_STROKE_PATH
        if do_fill:
            paint_mode |= VG_FILL_PATH
        style.paint_mode = paint_mode

        return style



length_pattern = re.compile(r"\s*(.+?)\s*(px|pt|pc|mm|cm|in)?\s*$", re.I)
def to_px(data):
    value, unit = length_pattern.match(data).groups()
    if "." in value:
        value = float(value)
    else:
        value = int(value)
    return value * SVG_PIXELS_PER_UNIT[unit]

def to_number(data):
    if "." in data or "e" in data or "E" in data:
        return float(data)
    else:
        return int(data)

hex_pattern = re.compile(r"#\s*([0-9A-F]{3,6})", re.I)
def to_rgb(data):
    original = data
    data = data.strip("\r\t\n ").lower()
    if data.startswith("rgb"):
        start = data.index("(") + 1
        end = data.rindex(")")
        s = data[start:end]
        R, G, B = [int(n) for n in s.split(",")]
    elif data.startswith("#"):
        s = hex_pattern.match(data).group(1)
        if len(s) == 3:
            R = int(s[0]*2, 16)
            G = int(s[1]*2, 16)
            B = int(s[2]*2, 16)
        elif len(s) == 6:
            R = int(s[0:2], 16)
            G = int(s[2:4], 16)
            B = int(s[4:6], 16)
        else:
            raise ValueError("Hex colors must be 3 or 6 digits")
    elif data in SVG_COLORS:
        R, G, B = SVG_COLORS[data]
    else:
        raise ValueError('Invalid color "%s"' % original)
    return (R, G, B)

transform_pattern = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\((.+?)\)", re.I)
def to_matrix(data):
    matrix = numpy.matrix([[1, 0, 0],
                           [0, 1, 0],
                           [0, 0, 1]])
    for action, arg_string in transform_pattern.findall(data):
        action = action.lower()
        args = [float(n) for n in re.split(r"(?:,|\s+)", arg_string)]

        if action == "matrix":
            a, b, c, d, e, f = args
            m = numpy.matrix([[a, b, 0],
                              [c, d, 0],
                              [e, f, 1]])
        elif action == "translate":
            tx = args[0]
            ty = args[0] if len(args) > 1 else 0.0
            m = numpy.matrix([[1,  0,  0],
                              [0,  1,  0],
                              [tx, ty, 1]])
        elif action == "scale":
            sx = args[0]
            sy = args[1] if len(args) > 1 else sx
            m = numpy.matrix([[sx, 0,  0],
                              [0,  sy, 0],
                              [0,  0,  1]])
        elif action == "rotate":
            a = args[0]
            rot = numpy.matrix([[ cos(a), sin(a), 0],
                                [-sin(a), cos(a), 0],
                                [ 0,      0,      1]])
            if len(args) > 1:
                cx = args[1]
                cy = args[2]
                t1 = numpy.matrix([[ 1,   0,  0],
                                   [ 0,   1,  0],
                                   [-cx, -cy, 1]])                
                t2 = numpy.matrix([[1,  0,  0],
                                   [0,  1,  0],
                                   [cx, cy, 1]])
                m = t1*rot*t2
            else:
                m = rot
        elif action == "skewx":
            t = tan(args[0])
            m = numpy.matrix([[1, 0, 0],
                              [t, 1, 0],
                              [0, 0, 0]])
        elif action == "skewy":
            t = tan(args[0])
            m = numpy.matrix([[1, t, 0],
                              [0, 1, 0],
                              [0, 0, 1]])

        matrix *= m

    return matrix.flatten().tolist()[0]


SVG_PIXELS_PER_UNIT = {None: 1, "px": 1, "pt": 1.25, "pc": 15,
                       "mm": 3.543307, "cm": 35.43307, "in": 90}

SVG_TAG_MAP = dict(svg=SVG, g=Group,
                   path=Path, rect=Rect, circle=Circle, ellipse=Ellipse,
                   line=Line, polyline=PolyLine, polygon=Polygon,
                   )

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

SVG_PATH_COMMANDS = dict(M=VG_MOVE_TO_ABS,   m=VG_MOVE_TO_REL,
                         Z=VG_CLOSE_PATH,    z=VG_CLOSE_PATH,
                         L=VG_LINE_TO_ABS,   l=VG_LINE_TO_REL,
                         H=VG_HLINE_TO_ABS,  h=VG_HLINE_TO_REL,
                         V=VG_VLINE_TO_ABS,  v=VG_VLINE_TO_REL,
                         C=VG_CUBIC_TO_ABS,  c=VG_CUBIC_TO_REL,
                         S=VG_SCUBIC_TO_ABS, s=VG_SCUBIC_TO_REL,
                         Q=VG_QUAD_TO_ABS,   q=VG_QUAD_TO_REL,
                         T=VG_SQUAD_TO_ABS,  t=VG_SQUAD_TO_REL)

SVG_COLORS = dict(aliceblue=(240, 248, 255),
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
                  lightgrey=(211, 211, 211),
                  lightpink=(255,182,193),
                  lightsalmon=(255,160,122),
                  lightseagreen=(32,178,170),
                  lightskyblue=(135,206,250),
                  lightslategray=(119,136,153),
                  lightslategrey=(119,136,153),
                  lightsteelblue=(176,196,222),
                  lightyellow=(255,255,224),
                  lime=(0,255,0),
                  limegreen=(50,205,50),
                  linen=(250,240,230),
                  magenta=(255,0,255),
                  maroon=(128,0,0),
                  mediumaquamarine=(102,205,170),
                  mediumblue=(0,0,205),
                  mediumorchid=(186,85,211),
                  mediumpurple=(147,112,219),
                  mediumseagreen=(60,179,113),
                  mediumslateblue=(123,104,238),
                  mediumspringgreen=(0,250,154),
                  mediumturquoise=(72,209,204),
                  mediumvioletred=(199,21,133),
                  midnightblue=(25,25,112),
                  mintcream=(245,255,250),
                  mistyrose=(255,228,225),
                  moccasin=(255,228,181),
                  navajowhite=(255,222,173),
                  navy=(0,0,128),
                  oldlace=(253,245,230),
                  olive=(128,128,0),
                  olivedrab=(107,142,35),
                  orange=(255,165,0),
                  orangered=(255,69,0),
                  orchid=(218,112,214),
                  palegoldenrod=(238,232,170),
                  palegreen=(152,251,152),
                  paleturquoise=(175,238,238),
                  palevioletred=(219,112,147),
                  papayawhip=(255,239,213),
                  peachpuff=(255,218,185),
                  peru=(205,133,63),
                  pink=(255,192,203),
                  plum=(221,160,221),
                  powderblue=(176,224,230),
                  purple=(128,0,128),
                  red=(255,0,0),
                  rosybrown=(188,143,143),
                  royalblue=(65,105,225),
                  saddlebrown=(139,69,19),
                  salmon=(250,128,114),
                  sandybrown=(244,164,96),
                  seagreen=(46,139,87),
                  seashell=(255,245,238),
                  sienna=(160,82,45),
                  silver=(192,192,192),
                  skyblue=(135,206,235),
                  slateblue=(106,90,205),
                  slategray=(112,128,144),
                  slategrey=(112,128,144),
                  snow=(255,250,250),
                  springgreen=(0,255,127),
                  steelblue=(70,130,180),
                  tan=(210,180,140),
                  teal=(0,128,128),
                  thistle=(216,191,216),
                  tomato=(255,99,71),
                  turquoise=(64,224,208),
                  violet=(238,130,238),
                  wheat=(245,222,179),
                  white=(255,255,255),
                  whitesmoke=(245,245,245),
                  yellow=(255,255,0),
                  yellowgreen=(154,205,50))
