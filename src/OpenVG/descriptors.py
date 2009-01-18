import numpy
import re

#Attribute descriptors so that we don't have to write getter functions
#for every single conversion.

class SVGDataType(object):
    update_on_change = False
    def __init__(self, key, default=None):
        self.key = key
        self.default = default
        
        self.value = None
        self.set = False

    def __get__(self, obj, type):
        if self.set:
            return self.value
        else:
            data = obj.get(self.key, self.default)
            self.value = self.fromstring(data)
            self.set = True

            return self.value

    def __set__(self, obj, value):
        self.value = value
        if self.update_on_change:
            obj.set(self.key, self.tostring(value))
        self.set = True

    def __delete__(self, obj):
        del obj.attrib[self.key]
        self.value = None
        self.set = False

    def write(self, obj):
        obj.set(self.key, self.tostring(self.value))

    def fromstring(self, data):
        raise NotImplementedError

    def tostring(self, value):
        raise NotImplementedError

class ListOf(SVGDataType):
    def __init__(self, datatype, key, default=None):
        SVGDataType.__init__(self, key, default)
        self.datatype = datatype

    def fromstring(self, data):
        if data is None:
            return None
        items = re.split(r"(?:,|\s+)", data.strip())
        return [self.datatype.fromstring(item) for item in items]

    def tostring(self, values):
        return ",".join(datatype.tostring(value) for value in values)

class Tuple(SVGDataType):
    def __init__(self, *descriptors):
        SVGDataType.__init__(self, None, None)
        self.descriptors = descriptors

    def __get__(self, obj, type):
        return tuple(desc.__get__(obj, type) for desc in self.descriptors)

    def __set__(self, obj, values):
        for desc,value in zip(self.descriptors, values):
            desc.__set__(obj, value)

    def write(self, obj):
        for desc in self.descriptors:
            desc.write(obj)

class Integer(SVGDataType):
    fromstring = staticmethod(int)
    tostring = staticmethod(str)

class Number(SVGDataType):
    @staticmethod
    def fromstring(data):
        try:
            return int(data)
        except:
            return float(data)

    @staticmethod
    def tostring(value):
        return str(value) if isinstance(value, int) else repr(value)

length_pattern = re.compile(r"\s*(.+?)\s*(px|pt|pc|mm|cm|in)?\s*$", re.I)
SVG_PIXELS_PER_UNIT = {None: 1, "px": 1, "pt": 1.25, "pc": 15,
                       "mm": 3.543307, "cm": 35.43307, "in": 90}

class Length(SVGDataType):
    valid_units = ["px","pt","mm","cm","in", "%"]
    def __init__(self, key, default=None, units="px"):
        SVGDataType.__init__(self, key, default)
        if units not in self.valid_units:
            raise ValueError("Invalid length unit '%s' specified on %s attribute"
                             % (units, key))
        self.units = units
        
    def fromstring(self, data):
        if data.endswith("%"):
            raise NotImplementedError("% lengths are not supported")
        value, units = length_pattern.match(data).groups()

        if units == self.units:
            return Number.fromstring(value)

        if self.units == "px":
            scale = SVG_PIXELS_PER_UNIT[units]
        else:
            scale = SVG_PIXELS_PER_UNIT[units]/SVG_PIXELS_PER_UNIT[self.units]
        
        return Number.fromstring(value) * scale

    def tostring(self, value):
        return Number.tostring(value) + self.units

Coordinate = Length

angle_pattern = re.compile(r"\s*(.+?)\s*(deg|grad|rad)?\s*$", re.I)
SVG_DEGREES_PER_UNIT = {None: 1, "deg": 1, "grad": 1.11, "rad":57.30}

class Angle(SVGDataType):
    valid_units = ["deg", "grad", "rad"]
    def __init__(self, key, default=None, units="deg"):
        SVGDataType.__init__(self, key, default)
        if units not in self.valid_units:
            raise ValueError("Invalid angle unit '%s' specified on %s attribute"
                             % (units, key))
        self.units = units

    def fromstring(self, data):
        value, units = angle_pattern.match(data).groups()

        if units == self.units:
            return Number.fromstring(value)

        if self.units == "deg":
            scale = SVG_DEGREES_PER_UNIT[units]
        else:
            scale = SVG_DEGREES_PER_UNIT[units]/SVG_DEGREES_PER_UNIT[self.units]
        
        return Number.fromstring(value) * scale

    def tostring(self, value):
        return Number.tostring(value) + self.units

hex_pattern = re.compile(r"#\s*([0-9A-F]{3,6})", re.I)
class Color(SVGDataType):
    @staticmethod
    def fromstring(data):
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
            raise ValueError('Unknown color "%s"' % original)
        
        return (R, G, B)

    @staticmethod
    def tostring(value):
        return "rgb(%d,%d,%d)" % value

class Paint(SVGDataType):
    pass


transform_pattern = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\((.+?)\)", re.I)
class TransformList(SVGDataType):
    @staticmethod
    def fromstring(data):
        if data is None:
            return None
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

    @staticmethod
    def tostring(value):
        a,b,w0,c,d,w1,e,f,w2 = value
        return "matrix(%r,%r,%r,%r,%r,%r)" % (a,b,c,d,e,f)


class URI(SVGDataType):
    pass

class Frequency(SVGDataType):
    pass

class Time(SVGDataType):
    pass

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
