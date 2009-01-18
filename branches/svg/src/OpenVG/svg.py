from math import cos, sin, tan, radians
import re

import numpy

from OpenVG import VG
from OpenVG import VGU
from OpenVG.font import load_font
from OpenVG.constants import *

__all__ = ["SVGElement", "SVGContainer", "SVGPrimitive",
           "SVG", "Group",
           "Path", "Rect", "Ellipse", "Circle", "Line", "PolyLine", "Polygon",
           "Text",
           "SVG_PATH_COMMANDS", "SVG_COLORS", "SVG_TAG_MAP", "SVG_PIXELS_PER_UNIT",
           ]

class SVGElement(object):
    def __init__(self, style, paint_mode, transform):
        self.style = style
        self.paint_mode = paint_mode
        self.transform = transform
        
    def load_style_from_element(self, e, immediate=True):
        if not immediate:
            style = DeferredStyle.from_element(e)
        else:
            style = DeferredStyle.from_element.im_func(VG.Style, e)
            if style.fill_paint:
                style.fill_paint = style.fill_paint[0](*style.fill_paint[1])
            if style.stroke_paint:
                style.stroke_paint = style.stroke_paint[0](*style.stroke_paint[1])
        self.style = style
        self.paint_mode = style.paint_mode

    def load_transform_from_element(self, e):
        if "transform" in e.attrib:
            self.transform = to_matrix(e.attrib["transform"])
        else:
            self.transform = None

    def draw(self):
        raise NotImplementedError

    def corners(self, transform=None):
        raise NotImplementedError

    def bounds(self, transform=None):
        (x1,y1), (x2,y2) = self.corners(transform)
        if x1 is y1 is x2 is y2 is None:
            return (0,0), (-1,-1)
        return (x1,y1), (x2-x1,y2-y1)

    @property
    def numpy_transform(self):
        T = numpy.matrix(self.transform)
        T.shape = (3,3)
        return T.T

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

    def load_children_from_element(self, e, immediate=True):
        for child in e.getchildren():
            child_cls = SVG_TAG_MAP.get(child.tag[child.tag.rfind("}") + 1:], None)
            if child_cls:
                if issubclass(child_cls, SVG):
                    self.children.append(child_cls.from_element(child, immediate, flip=False))
                else:
                    self.children.append(child_cls.from_element(child, immediate))

    def corners(self, transform=None):
        minx,miny, maxx,maxy = None,None, None,None
        for child in self.children:
            (x1,y1), (x2,y2) = child.corners(transform)
            if x1 < minx or minx is None: minx = x1
            if y1 < miny or miny is None: miny = y1

            if x2 > maxx: maxx = x2
            if y2 > maxy: maxy = y2

        if self.transform is None or minx is miny is maxx is maxy is None:
            return (minx, miny), (maxx, maxy)
        else:
            pts = numpy.matrix([[minx, minx, maxx, maxx],
                                [miny, maxy, maxy, miny],
                                [1,    1,    1,    1]])
            corners = self.numpy_transform * pts

            X,Y = corners[0], corners[1]
            return (X.min(), Y.min()), (X.max(), Y.max())

class SVGPrimitive(SVGElement):
    def __init__(self, style, paint_mode, transform):
        SVGElement.__init__(self, style, paint_mode, transform)
        self._path = None

    def draw(self, paint_mode=VG_STROKE_PATH):
        if self.transform:
            mat = VG.get_matrix()
            VG.mult_matrix(self.transform)
            
        if self.paint_mode:
            paint_mode = self.paint_mode
        
        self.path.draw(paint_mode, style=self.style)

        if self.transform:
            VG.load_matrix(mat)

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

    def corners(self, transform=None):
        (x1,y1), (w,h) = self.path.bounds()
        x2 = x1 + w
        y2 = y1 + h
        
        if self.transform:
            if transform is not None:
                transform = self.numpy_transform * transform
            else:
                transform = self.numpy_transform

        if transform is None:
            return (x1,y1), (x2,y2)
        else:
            pts = numpy.matrix([[x1, x1, x2, x2],
                                [y1, y2, y2, y1],
                                [1,  1,  1,  1]])
            corners = transform * pts

            X,Y = corners[0], corners[1]
            return (X.min(), Y.min()), (X.max(), Y.max())

    path = property(get_path, set_path)

class SVG(SVGContainer):
    def __init__(self, children, width, height, viewbox=None, flip=True):
        SVGContainer.__init__(self, children, None, VG_STROKE_PATH, None)
        self.width = width
        self.height = height
        self.viewbox = viewbox
        self.transform = None
        if self.children:
            self.setup_transform(flip)

    def setup_transform(self, flip):
        sx = sy = 1
        vx = vy = 0
        if self.viewbox:
            (vx,vy), (vw,vh) = self.viewbox
            if self.width or self.height:
                sx = self.width/float(vw) if self.width else self.height/float(vh)
                sy = self.height/float(vh) if self.height else self.width/float(vw)
            else:
                (bx, by), (bw, bh) = self.bounds()
                sx = bw/float(vw)
                sy = bh/float(vh)
                

        if flip:
            sy = -sy
            vy += self.height
        self.transform = [ sx, 0,   0,
                           0,  sy,  0,
                          -vx, vy,  1]

    @classmethod
    def from_element(cls, e, immediate=True, flip=True):
        
        width = to_px(e.get("width", "0px"))
        height = to_px(e.get("height", "0px"))
        if "viewBox" in e.attrib:
            x,y, w,h = e.attrib["viewBox"].split()
            viewbox = ((to_px(x), to_px(y)), (to_px(w), to_px(h)))
        else:
            viewbox = None
        svg = cls([], width, height, viewbox)
        svg.load_children_from_element(e, immediate)
        svg.setup_transform(flip)

        return svg

class Group(SVGContainer):
    @classmethod
    def from_element(cls, e, immediate=True):
        g = cls([], None, None, None)
        g.load_style_from_element(e, immediate)
        g.load_transform_from_element(e)
        
        g.load_children_from_element(e, immediate)

        return g

class Path(SVGPrimitive):
    def __init__(self, data, style=None, paint_mode=None, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.data = data

    def build_path(self):
        path = VG.Path()
        path.extend(self.data)
        return path

    @classmethod
    def from_element(cls, e, immediate=True):
        try:
            segments = list(to_commands(e.attrib["d"]))
        except KeyError:
            segments = []

        path = cls(segments, None, None, None)
        path.load_style_from_element(e, immediate)
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

    @classmethod
    def from_element(cls, e, immediate=True):
        x = to_px(e.get("x", "0"))
        y = to_px(e.get("y", "0"))
        width = to_px(e.attrib["width"])
        height = to_px(e.attrib["height"])
        rx = to_px(e.get("rx", "0"))
        ry = to_px(e.get("ry", "0"))
        if rx or ry:
            if rx and not ry: ry = rx
            if ry and not rx: rx = ry
        rect = cls((x,y), width, height, rx, ry)
        rect.load_style_from_element(e, immediate)
        rect.load_transform_from_element(e)
        return rect
        

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

    @classmethod
    def from_element(cls, e, immediate=True):
        cx = to_px(e.get("cx", "0"))
        cy = to_px(e.get("cy", "0"))
        rx = to_px(e.attrib["rx"])
        ry = to_px(e.attrib["ry"])

        ellipse = cls((cx,cy), rx, ry)
        ellipse.load_style_from_element(e, immediate)
        ellipse.load_transform_from_element(e)

        return ellipse
        

class Circle(Ellipse):
    def __init__(self, pos, radius, style=None, paint_mode=None, transform=None):
        Ellipse.__init__(self, pos, radius, radius, style, paint_mode, transform)

    def get_radius(self):
        return self.rx

    def set_radius(self, value):
        self.rx = self.ry = value

    @classmethod
    def from_element(cls, e, immediate=True):
        cx = to_px(e.get("cx", "0"))
        cy = to_px(e.get("cy", "0"))
        r = to_px(e.attrib["r"])

        circle = cls((cx,cy), r)
        circle.load_style_from_element(e, immediate)
        circle.load_transform_from_element(e)

        return circle

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

    @classmethod
    def from_element(cls, e, immediate=True):
        x1 = to_px(e.attrib["x1"])
        y1 = to_px(e.attrib["y1"])

        x2 = to_px(e.attrib["x2"])
        y2 = to_px(e.attrib["y2"])

        line = cls((x1,y1),(x2,y2))
        line.load_style_from_element(e, immediate)
        line.load_transform_from_element(e)

        return line

class PolyLine(SVGPrimitive):
    def __init__(self, points, closed=False, style=None, paint_mode=None, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.points = points
        self.closed = closed

    def build_path(self):
        path = VG.Path()
        #VGU.polygon(path, self.points, self.closed)
        #ShivaVG's implementation of vguPolygon reuses a function that
        #assumes that there are at most 26 data points (26 being the
        #most number needed by other vgu functions) to append polygon
        #data, which then fails the assert if there are more than 13 points
        #The workaround is to just not use the VGU function

        path.move_to(self.points[0])
        for point in self.points[1:]:
            path.line_to(point)

        if self.closed:
            path.close()

        return path

    @classmethod
    def from_element(cls, e, immediate=True):
        coords = map(to_px, re.split(r"(?:,|\s+)", e.attrib["points"]))
        points = [(coords[i], coords[i+1]) for i in xrange(0, len(coords), 2)]

        polyline = cls(points)
        polyline.load_style_from_element(e, immediate)
        polyline.load_transform_from_element(e)

        return polyline

class Polygon(PolyLine):
    def __init__(self, points, style=None, paint_mode=None, transform=None):
        PolyLine.__init__(self, points, True, style, paint_mode, transform)

class Text(SVGPrimitive):
    def __init__(self, x, y, dx, dy, text, font_face, style=None, paint_mode=VG_FILL_PATH, transform=None):
        SVGPrimitive.__init__(self, style, paint_mode, transform)
        self.text = text
        self.x = x
        self.y = y
        self.font = font_face

    def build_path(self):
        text = self.font.build_path(self.text)

        (x,y), (w,h) = text.bounds()

        mat = VG.get_matrix()
        VG.load_matrix([1,0,0,0,-1,0,self.x[0],self.y[0],1])

        path = VG.Path()
        text.transform(path)

        VG.load_matrix(mat)

        return path

    @classmethod
    def from_element(cls, e, immediate=True):
        x = map(to_px, re.split(r"(?:,|\s+)", e.get("x","0")))
        y = map(to_px, re.split(r"(?:,|\s+)", e.get("y","0")))
        dx = map(to_px, re.split(r"(?:,|\s+)", e.get("dx","0")))
        dy = map(to_px, re.split(r"(?:,|\s+)", e.get("dy","0")))

        name = e.get("font-family", "freesansbold")

        font = load_font(name, to_pt(e.get("font-size", "20")))
        
        text = cls(x, y, dx, dy, e.text.strip(), font)
        text.load_style_from_element(e, immediate)
        text.load_transform_from_element(e)

        return text
        

style_pattern = re.compile(r"(\w+-?\w+)\s*:\s*([^;]+)(?:;|$)")
class DeferredStyle(VG.Style):
    def __init__(self, **kwargs):
        VG.Style.__init__(self, **kwargs)
        self.initialized = False
        self.paint_mode = VG_STROKE_PATH
        
    def enable(self):
        if not self.initialized:
            self.initialize()
        VG.Style.enable(self)

    def initialize(self):
        if not self.initialized:
            if self.fill_paint:
                const, args = self.fill_paint
                self.fill_paint = const(*args)
            if self.stroke_paint:
                const, args = self.stroke_paint
                self.stroke_paint = const(*args)
            self.initialized = True

    @classmethod
    def from_element(cls, e):
        style = cls()
        
        do_fill = False
        do_stroke = False

        fill_opacity = 1.0
        stroke_opacity = 1.0
        
        for name, value in style_pattern.findall(e.get("style","")) + e.attrib.items():
            name = name.lower().strip()
            value = value.lower().strip()
            if name == "fill":
                if value == "none":
                    do_fill = False
                else:
                    do_fill = True
                    r,g,b = to_rgb(value)
                    style.fill_paint = [VG.ColorPaint, [(r,g,b,fill_opacity)]]
            elif name == "fill-opacity":
                fill_opacity = to_number(value)
                if do_fill:
                    r,g,b,a = style.fill_paint[1][0]
                    style.fill_paint[1][0] = (r,g,b,fill_opacity)
            elif name == "stroke":
                if value == "none":
                    do_stroke = False
                else:
                    do_stroke = True
                    r,g,b = to_rgb(value)
                    style.stroke_paint = [VG.ColorPaint, [(r,g,b,stroke_opacity)]]
            elif name == "stroke-opacity":
                stroke_opacity = to_number(value)
                if do_stroke:
                    r,g,b,a = style.stroke_paint[1][0]
                    style.stroke_paint[1][0] = (r,g,b,stroke_opacity)
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
                    style[VG_STROKE_DASH_PATTERN] = map(to_number, re.split(r"(?:\s*,\s*)|(?:\s*|,)", value))
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

def load_svg_element(e, immediate=True):
    try:
        cls = SVG_TAG_MAP[e.tag[e.tag.rfind("}") + 1:]]
    except:
        raise ValueError('Unable to load tag %r' % e.tag[e.tag.rfind("}") + 1:]) 
    return cls.from_element(e, immediate)

length_pattern = re.compile(r"\s*(.+?)\s*(px|pt|pc|mm|cm|in)?\s*$", re.I)
def to_px(data):
    value, unit = length_pattern.match(data).groups()
    if "." in value:
        value = float(value)
    else:
        value = int(value)
    return value * SVG_PIXELS_PER_UNIT[unit]

def to_pt(data):
    value, unit = length_pattern.match(data).groups()
    if "." in value:
        value = float(value)
    else:
        value = int(value)
    if not unit:
        return value
    else:
        return value * SVG_PIXELS_PER_UNIT[unit] * 0.8

def to_number(data):
    data = data.strip()
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
    return (R/255.0, G/255.0, B/255.0)

path_pattern = re.compile(r"([MZLHVCSQTA])([^MZLHVCSQTA]+)", re.IGNORECASE)
def to_commands(data):
    for command, args in path_pattern.findall(data):
        command = command.strip()
        if command == "A" or command == "a":
            rel = command == "a"
            coords = map(to_number, re.split(r"(?:,|\s+)", args.strip()))
            if len(coords) % 7:
                raise ValueError("Incorrect number of arguments for arc command (expected 7)")
            for i in xrange(len(coords)//7):
                large, sweep = coords[i*7+3], coords[i*7+4]
                vg_command = SVG_ARC_COMMANDS[(large, sweep)] | rel
                yield (vg_command, coords[i*7:i*7+3]+coords[i*7+5:i*7+7])
        else:
            vg_command = SVG_PATH_COMMANDS[command]
            if vg_command == VG_CLOSE_PATH:
                yield (vg_command, ())
                continue
            coords = map(to_number, re.split(r"(?:,|\s+)", args.strip()))

            count = arg_count(vg_command)
            if len(coords) % count:
                raise ValueError("Incorrect number of arguments for command %s" % command)
            if vg_command - (vg_command % 2) == VG_MOVE_TO and count > 2:
                yield (vg_command, coords[:2])
                count -= 2
                del coords[:2]
                vg_command = VG_LINE_TO | (vg_command & VG_RELATIVE)

            for i in xrange(len(coords)/count):
                yield (vg_command, coords[i*count:(i+1)*count])

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
            ty = args[1] if len(args) > 1 else 0.0
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
            a = radians(args[0])
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
                m = t2*rot*t1
            else:
                m = rot
        elif action == "skewx":
            t = tan(radians(args[0]))
            m = numpy.matrix([[1, 0, 0],
                              [t, 1, 0],
                              [0, 0, 0]])
        elif action == "skewy":
            t = tan(radians(args[0]))
            m = numpy.matrix([[1, t, 0],
                              [0, 1, 0],
                              [0, 0, 1]])

        matrix = m * matrix

    return matrix.flatten().tolist()[0]


SVG_PIXELS_PER_UNIT = {None: 1, "px": 1, "pt": 1.25, "pc": 15,
                       "mm": 3.543307, "cm": 35.43307, "in": 90}

SVG_TAG_MAP = dict(svg=SVG, g=Group,
                   path=Path, rect=Rect, circle=Circle, ellipse=Ellipse,
                   line=Line, polyline=PolyLine, polygon=Polygon,
                   text=Text,
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

SVG_ARC_COMMANDS = {(False, True):VG_SCCWARC_TO,
                    (False, False):VG_SCWARC_TO,
                    (True, True):VG_LCCWARC_TO,
                    (True, False):VG_LCWARC_TO}

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
