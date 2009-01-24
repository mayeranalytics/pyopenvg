from math import cos, sin, tan, radians, atan2
import re

from xml.etree import ElementTree
import numpy

from OpenVG import VG
from OpenVG import VGU
from OpenVG.font import load_font
from OpenVG.constants import *

from OpenVG import descriptors as desc

__all__ = ["SVGElement", "SVGDrawableElement", "SVGContainer", "SVGPrimitive",
           "SVG", "Group",
           "Path", "Rect", "Ellipse", "Circle", "Line", "PolyLine", "Polygon",
           "Text",
           "SVGElementFactory", "SVGElementTree", "parse_svg"]

#ElementTree kludge for outputting svg instead of ns0
ElementTree._namespace_map["http://www.w3.org/2000/svg"] = "svg"

def SVGElementFactory(tag, attrib):
    factory = SVG_TAG_MAP.get(tag[tag.rfind("}")+1:], SVGElement)
    return factory(tag, attrib)

class SVGElementTree(object, ElementTree.ElementTree):
    def __init__(self, *args, **kwargs):
        ElementTree.ElementTree.__init__(self, *args, **kwargs)
        self.id_table = {}
        
    def write(self, *args, **kwargs):
        for e in self.getiterator():
            if isinstance(e, SVGElement):
                e.dump()
        ElementTree.ElementTree.write(self, *args, **kwargs)

    def init(self):
        for e in self.getiterator():
            if e.get("id"):
                self.id_table[e.get("id")] = e

        self.getroot().init(id_table=self.id_table)

class SVGElement(ElementTree._ElementInterface):
    _attributes = {}
    def __init__(self, *args, **kwargs):
        ElementTree._ElementInterface.__init__(self, *args, **kwargs)
        self.initialized = False
    
    def init(self, id_table=None):
        for key, desc in self._attributes.iteritems():
            setattr(self, key, desc.load(self))
        self.initialized = True
        self.id_table = id_table

        for child in self:
            if not child.initialized:
                child.init(id_table=id_table)

    def dump(self):
        for key, desc in self._attributes.iteritems():
            desc.dump(self, getattr(self, key))
        
    def __repr__(self):
        return "<%s %s at %x>" % (self.__class__.__name__, self.tag, id(self))
    
    def makeelement(self, tag, attrib):
        return SVGElementFactory(tag, attrib)

class SVGDrawableElement(SVGElement):
    _attributes = dict(
        transform=desc.TransformList("transform"))

    def init(self, do_stroke=False, do_fill=False, id_table=None):
        for key, desc in self._attributes.iteritems():
            setattr(self, key, desc.load(self))
        self.initialized = True
        self.id_table = id_table
        
        if self.transform is not None:
            T = numpy.matrix(self.transform)
            T.shape = (3,3)
            self.numpy_transform = T.T
        else:
            self.numpy_transform = None

    def get_style(self, do_stroke=False, do_fill=False):
        if has_style(self.keys()):
            if "style" in self.keys():
                attrs = style_pattern.findall(self.get("style"))
            else:
                attrs = []
            attrs.extend(self.items())
            style = to_style(self, attrs, do_stroke, do_fill)
            paint_mode = style.paint_mode
        else:
            style = None
            paint_mode = 0
            if do_stroke:
                paint_mode |= VG_STROKE_PATH
            if do_fill:
                paint_mode |= VG_FILL_PATH
        return style, paint_mode

    def dump(self):
        SVGElement.dump(self)
        #TODO: add style writing code

    def draw(self):
        raise NotImplementedError

    def corners(self, transform=None):
        raise NotImplementedError

    def bounds(self, transform=None):
        (x1,y1), (x2,y2) = self.corners(transform)
        if x1 is y1 is x2 is y2 is None:
            return (0,0), (-1,-1)
        return (x1,y1), (x2-x1,y2-y1)

    

class SVGContainer(SVGDrawableElement):
    def init(self, do_stroke=False, do_fill=False, id_table=None):
        SVGDrawableElement.init(self, do_stroke, do_fill, id_table)

        self.style, self.paint_mode = self.get_style(do_stroke, do_fill)
        
        do_stroke = self.paint_mode & VG_STROKE_PATH
        do_fill = self.paint_mode & VG_FILL_PATH
        
        self.drawables = []
        for child in self:
            if not child.initialized:
                if isinstance(child, SVGDrawableElement):
                    child.init(do_stroke, do_fill, id_table)
                    self.drawables.append(child)
                else:
                    child.init(id_table)

    def draw(self):
        if self.transform:
            mat = VG.get_matrix()
            VG.mult_matrix(self.transform)

        if self.style:
            self.style.enable()

        for child in self.drawables:
            child.draw()

        if self.style:
            self.style.disable()
        
        if self.transform:
            VG.load_matrix(mat)

    def corners(self, transform=None):
        minx,miny, maxx,maxy = None,None, None,None
        if not self.drawables:
            return (None,None), (None,None)
        
        for child in self.drawables:
            (x1,y1), (x2,y2) = child.corners(transform)
            if x1 is y1 is x2 is y2 is None:
                continue
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

class SVGPrimitive(SVGDrawableElement):
    def init(self, do_stroke=False, do_fill=False, id_table=None):
        SVGDrawableElement.init(self, do_stroke, do_fill, id_table)
        self.path = self.build_path() 
        self.style, self.paint_mode = self.get_style(do_stroke, do_fill)

    def draw(self):
        if self.transform:
            mat = VG.get_matrix()
            VG.mult_matrix(self.transform)

        self.path.draw(self.paint_mode, style=self.style)

        if self.transform:
            VG.load_matrix(mat)

    def build_path(self):
        raise NotImplementedError

    def corners(self, transform=None):
        (x1,y1), (w,h) = self.path.bounds()
        x2 = x1 + w
        y2 = y1 + h
        
        if self.transform is not None:
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

class SVG(SVGContainer):
    _attributes = dict(
        transform = desc.TransformList("transform"),
        width = desc.Length("width", default="0px"),
        height = desc.Length("height", default="0px"),
        viewbox = desc.ListOf(desc.Length(None, default="0px"), "viewBox"))

    def setup_transform(self, flip):
        sx = sy = 1
        vx = vy = 0
        if self.viewbox:
            (vx,vy,vw,vh) = self.viewbox
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

        self.numpy_transform = numpy.matrix(self.transform)
        self.numpy_transform.shape = (3,3)
        self.numpy_transform = self.numpy_transform.T

    def fit(self, width, height):
        w,h = self.bounds()[1]
        s = 1.0
        if w > width:
            s = width/w
        if h*s > height:
            s = height/h
        T2 = numpy.matrix([[s, 0, 0],
                           [0, s, 0],
                           [0, 0, 1]])
        self.numpy_transform = self.numpy_transform * T2
        self.transform = self.numpy_transform.T.flatten().tolist()[0]

class Group(SVGContainer):
    pass

class Path(SVGPrimitive):
    def build_path(self):
        path = VG.Path()
        path.extend(self.segments)
        return path

    @property
    def segments(self):
        return list(to_commands(self.get("d")))

class Rect(SVGPrimitive):
    def build_path(self):
        path = VG.Path()
        rx = self.rx
        ry = self.ry
        if rx is ry is None:
            VGU.rect(path, self.position, (self.width, self.height))
        else:
            if rx is None:
                rx = ry
            elif ry is None:
                ry = rx
            if rx > self.width/2.0:
                rx = self.width/2.0
            if ry > self.height/2.0:
                ry = self.height/2.0
            VGU.round_rect(path, self.position, (self.width, self.height), rx, ry)
        return path
    _attributes = dict(
        transform = desc.TransformList("transform"),
        position = desc.Tuple(desc.Coordinate("x", default="0"),
                              desc.Coordinate("y", default="0")),

        width = desc.Length("width", default="0"),
        height = desc.Length("height", default="0"),
        
        rx = desc.Length("rx"),
        ry = desc.Length("ry"))

class Ellipse(SVGPrimitive):
    def build_path(self):
        path = VG.Path()
        VGU.ellipse(path, (self.cx, self.cy), (self.rx*2, self.ry*2))
        return path
    _attributes = dict(
        transform = desc.TransformList("transform"),
        cx = desc.Coordinate("cx", default="0"),
        cy = desc.Coordinate("cy", default="0"),

        rx = desc.Length("rx"),
        ry = desc.Length("ry"))

class Circle(SVGPrimitive):
    def build_path(self):
        path = VG.Path()
        VGU.ellipse(path, (self.cx, self.cy), (self.r*2, self.r*2))
        return path
    _attributes = dict(
        transform = desc.TransformList("transform"),
        cx = desc.Coordinate("cx", default="0"),
        cy = desc.Coordinate("cy", default="0"),

        r = desc.Length("r"))

class Line(SVGPrimitive):
    def build_path(self):
        path = VG.Path()
        VGU.line(path, (self.x1, self.y1), (self.x2, self.y2))
        return path

    _attributes = dict(
        transform = desc.TransformList("transform"),
        x1 = desc.Coordinate("x1", default="0"),
        y1 = desc.Coordinate("y1", default="0"),
        x2 = desc.Coordinate("x2", default="0"),
        y2 = desc.Coordinate("y2", default="0"))
    

class PolyLine(SVGPrimitive):
    closed = False
    
    def build_path(self):
        path = VG.Path()
        #VGU.polygon(path, self.points, self.closed)
        #ShivaVG's implementation of vguPolygon reuses a function that
        #assumes that there are at most 26 data points (26 being the
        #most number needed by other vgu functions) to append polygon
        #data, which then fails the assert if there are more than 13 points
        #The workaround is to just not use the VGU function

        if self.points:
            path.move_to((self.points[0], self.points[1]))
            
        for i in xrange(2, len(self.points), 2):
            path.line_to((self.points[i], self.points[i+1]))

        if self.closed:
            path.close()

        return path

    _attributes = dict(
        transform = desc.TransformList("transform"),
        points = desc.ListOf(desc.Coordinate(None), "points"))

class Polygon(PolyLine):
    closed = True

class Text(SVGPrimitive):
    def build_path(self):
        text = self.font.build_path(self.text)

        (x,y), (w,h) = text.bounds()

        mat = VG.get_matrix()
        VG.load_matrix([1,0,0,0,-1,0,self.x[0],self.y[0],1])

        path = VG.Path()
        text.transform(path)

        VG.load_matrix(mat)

        return path

    _attributes = dict(
        transform = desc.TransformList("transform"),
        x = desc.ListOf(desc.Coordinate(None), "x", default="0"),
        y = desc.ListOf(desc.Coordinate(None), "y", default="0"),
        dx = desc.ListOf(desc.Coordinate(None), "dx", default="0"),
        dy = desc.ListOf(desc.Coordinate(None), "dy", default="0"),

        font_size = desc.Length("font-size", default="16pt", units="pt"))

    @property
    def font(self):
        name = self.get("font-family", "freesansbold")

        return load_font(name, self.font_size)


class Gradient(SVGElement):
    linear = True
    def init(self, id_table=None):
        SVGElement.init(self, id_table) 
        self.stops = self.get_stops()
        if self.href:
            href = self.id_table[self.href[1:]]
            if not href.initialized:
                href.init(self.id_table)
            if not self.stops:
                self.stops = href.stops
            if not self.get("spreadMode"):
                self.spread = href.spread

    def get_stops(self):
        stops = []
        last_offset = None
        for child in self:
            if child.tag.endswith("stop"):
                if child.get("offset").endswith("%"):
                    offset = float(child.get("offset")[:-1])/100.0
                else:
                    offset = desc.Number.fromstring(child.get("offset"))

                if last_offset is not None and last_offset > offset:
                    offset = last_offset
                last_offset = offset

                opacity = desc.Number.fromstring(child.get("stop-opacity", "1"))
                if child.get("style"):
                    for name, value in style_pattern.findall(child.get("style")):
                        if name == "stop-color":
                            R,G,B = desc.Color.fromstring(value)
                        elif name == "stop-opacity":
                            opacity = desc.Number.fromstring(value)
                if child.get("stop-color"):
                    R,G,B = desc.Color.fromstring(child.get("stop-color"))
                
                stops.append((offset, (R/255.0, G/255.0, B/255.0, opacity)))
        return stops

    def build_paint(self, element):
        if self.spread == "pad":
            spread = VG_COLOR_RAMP_SPREAD_PAD
        elif self.spread == "repeat":
            spread = VG_COLOR_RAMP_SPREAD_REPEAT
        elif self.spread == "reflect":
            spread = VG_COLOR_RAMP_SPREAD_REFLECT
        else:
            raise ValueError("invalid spreadMethod '%s' specified" % self.spread)

        vector = self.get_vector(element)

        paint = VG.GradientPaint(vector, self.linear)
        paint.stops = self.stops
        paint.spread_mode = spread
        paint.transform = self.transform

        return paint

    def get_vector(self, element):
        raise NotImplementedError
        
class LinearGradient(Gradient):
    linear = True
    _attributes = dict(
        transform = desc.TransformList("gradientTransform"),
        units = desc.String("gradientUnits", default="objectBoundingBox"),

        x1 = desc.String("x1", default="0%"),
        y1 = desc.String("y1", default="0%"),
        x2 = desc.String("x2", default="100%"),
        y2 = desc.String("y2", default="0%"),

        spread = desc.String("spreadMethod", default="pad"),
        href = desc.String("{http://www.w3.org/1999/xlink}href"))

    def get_vector(self, element):
        to_px = desc.Coordinate(None, units="px").fromstring
        if self.units == "objectBoundingBox":
            (x0,y0), (w,h) = element.bounds()
            if "%" in self.x1:
                x1 = x0 + desc.Percentage.fromstring(self.x1)*w
            else:
                x1 = x0 + to_px(self.x1)
            if "%" in self.x2:
                x2 = x0 + desc.Percentage.fromstring(self.x2)*w
            else:
                x2 = x0 + to_px(self.x2)
            if "%" in self.y1:
                y1 = y0 + desc.Percentage.fromstring(self.y1)*h
            else:
                y1 = y0 + to_px(self.y1)
            if "%" in self.y2:
                y2 = y0 + desc.Percentage.fromstring(self.y2)*h
            else:
                y2 = y0 + to_px(self.y2)

            return ((x1,y1), (x2,y2))
        elif self.units == "userSpaceOnUse":
            return ((to_px(self.x1), to_px(self.y1)), (to_px(self.x2), to_px(self.y2)))
        else:
            raise ValueError("Invalid gradientUnits '%s' specified" % self.units)
        
class RadialGradient(Gradient):
    linear = False
    _attributes = dict(
        transform = desc.TransformList("gradientTransform"),
        units = desc.String("gradientUnits", default="objectBoundingBox"),

        cx = desc.String("cx", default="50%"),
        cy = desc.String("cy", default="50%"),
        
        fx = desc.String("fx"),
        fy = desc.String("fy"),

        radius = desc.String("r", default="50%"),

        spread = desc.String("spreadMethod", default="pad"),
        href = desc.String("{http://www.w3.org/1999/xlink}href"))

    def init(self, id_table=None):
        Gradient.init(self, id_table)
        if self.fx is None:
            self.fx = self.cx
        if self.fy is None:
            self.fy = self.cy

    def get_vector(self, element):
        to_px = desc.Coordinate(None, units="px").fromstring
        if self.units == "objectBoundingBox":
            (x0,y0), (w,h) = element.bounds()
            if "%" in self.fx:
                fx = x0 + desc.Percentage.fromstring(self.fx)*w
            else:
                fx = x0 + to_px(self.fx)
            if "%" in self.fy:
                fy = y0 + desc.Percentage.fromstring(self.fy)*h
            else:
                fy = y0 + to_px(self.fy)
            
            if "%" in self.cx:
                cx = x0 + desc.Percentage.fromstring(self.cx)*w
            else:
                cx = x0 + to_px(self.cx)
            if "%" in self.cy:
                cy = y0 + desc.Percentage.fromstring(self.cy)*h
            else:
                cy = y0 + to_px(self.cy)

            if "%" in self.radius:
                r = desc.Percentage.fromstring(self.radius)*w
            else:
                r = to_px(self.radius)

            if (fx-cx)**2 + (fy-cy)**2 > r**2:
                angle = atan2(fy-cy, fx-cx)
                fx = cx + r*cos(angle)
                fy = cy + r*sin(angle)

            return ((cx,cy), (fx,fy), r)
        elif self.units == "userSpaceOnUse":
            return ((to_px(self.cx), to_px(self.cy)),
                    (to_px(self.cx), to_px(self.cy)),
                    to_px(self.radius))
        else:
            raise ValueError("Invalid gradientUnits '%s' specified" % self.units)

    

def parse_svg(source, init=True):
    svg_tree_builder = ElementTree.TreeBuilder(SVGElementFactory)
    parser = ElementTree.XMLTreeBuilder(target=svg_tree_builder)
    
    tree = SVGElementTree()
    tree.parse(source, parser)

    if init:
        tree.init()
        if isinstance(tree.getroot(), SVG):
            tree.getroot().setup_transform(True)
    
    return tree


style_properties = ["fill", "fill-opacity", "fill-rule",
                    "stroke", "stroke-opacity", "stroke-width",
                    "stroke-dasharray", "stroke-dashoffset",
                    "stroke-linecap", "stroke-linejoin", "stroke-miterlimit"]

def has_style(keys):
    if "style" in keys:
        return True
    return any(key in style_properties for key in keys)

style_pattern = re.compile(r"(\w+-?\w+)\s*:\s*([^;]+)(?:;|$)")
to_px = desc.Length(None, units="px").fromstring
def to_style(element, attrs, do_stroke=False, do_fill=False):
    style = VG.Style()

    fill_opacity = stroke_opacity = opacity = 1.0
    
    for name, value in attrs:
        name = name.lower().strip()
        value = value.strip()
        if name == "fill":
            if value == "none":
                do_fill = False
            else:
                do_fill = True
                style.fill_paint = desc.Paint.fromstring(value, element)
        elif name == "fill-opacity":
            fill_opacity = desc.Number.fromstring(value) * opacity
        elif name == "stroke":
            if value == "none":
                do_stroke = False
            else:
                do_stroke = True
                style.stroke_paint = desc.Paint.fromstring(value, element)
        elif name == "stroke-opacity":
            stroke_opacity = desc.Number.fromstring(value) * opacity
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
                style[VG_STROKE_DASH_PATTERN] = map(to_px, re.split(r"(?:\s*,\s*)|(?:\s*|,)", value))
        elif name == "fill-rule":
            if value == "evenodd":
                style[VG_FILL_RULE] = VG_EVEN_ODD
            elif value == "nonzero":
                style[VG_FILL_RULE] = VG_NON_ZERO
        elif name == "opacity":
            opacity = desc.Number.fromstring(value)
            fill_opacity *= opacity
            stroke_opacity *= opacity

    if do_fill and isinstance(style.fill_paint, VG.ColorPaint):
        style.fill_paint.opacity = fill_opacity
        
    if do_stroke and isinstance(style.stroke_paint, VG.ColorPaint):
        style.stroke_paint.opacity = stroke_opacity            


    paint_mode = 0
    if do_stroke:
        paint_mode |= VG_STROKE_PATH
    if do_fill:
        paint_mode |= VG_FILL_PATH
    style.paint_mode = paint_mode

    return style

path_pattern = re.compile(r"([MZLHVCSQTA])([^MZLHVCSQTA]+)", re.IGNORECASE)
def to_commands(data):
    for command, args in path_pattern.findall(data):
        command = command.strip()
        if command == "A" or command == "a":
            rel = command == "a"
            coords = map(float, re.split(r"(?:,|\s+)", args.strip()))
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
            coords = map(float, re.split(r"(?:,|\s+)", args.strip()))

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

SVG_TAG_MAP = dict(svg=SVG, g=Group, path=Path, rect=Rect, text=Text,
                   ellipse=Ellipse, circle=Circle,
                   line=Line, polyline=PolyLine, polygon=Polygon,
                   linearGradient=LinearGradient, radialGradient=RadialGradient)

