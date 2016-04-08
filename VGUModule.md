# Introduction #

VGU is to OpenVG what GLU is to OpenGL - it provides some handy functions that you would otherwise end up writing yourself anyways. It is not guaranteed to be provided, but it probably will be since it's fairly straight-forward.

# Drawing Primitives #

VGU supplies several functions to draw basic primitives to make you life easier:

  * **line(path, p1, p2)** - appends a line segment from p1 to p2 to path
  * **polygon(path, points, closed=True)** - appends a polygon with points p to path
  * **rect(path, pos, dimensions)** - appends a rectangle with its bottom-left corner at pos and with the supplied dimensions
  * **round\_rect(path, pos, dimensions, arc\_width, arc\_height)** - appends a rounded rectangle with its bottom-left corner at pos with the supplied dimensions and with corners with the supplied arc\_width and height.
  * **ellipse(path, center, dimensions)** - appends an ellipse centered at center with the supplied dimensions. For a circle, use (2\*radius, 2\*radius) for the dimensions.
  * **arc(path, pos, dimensions, start\_angle, angle\_extent, arc\_type)** - appends either a regular arc, a chord, or a sector (pie shape). The angles are specified in degrees. arc\_type must be an enum from:

```
typedef enum {
  VGU_ARC_OPEN                                 = 0xF100,
  VGU_ARC_CHORD                                = 0xF101,
  VGU_ARC_PIE                                  = 0xF102
} VGUArcType;
```

# Computing Warp Matrices #

VGU also provides functions to compute the appropriate matrix for transforming the drawing surface from one shape to another:

**compute\_warp\_quad\_to\_square(p1, p2, p3, p4)** - returns a matrix that maps an arbitrary quadrilateral defined by points p1, p2, p3, and p4 to the unit square.

```
   p2 _______ p3      0,1 ______ 1,1
     /      /            |      |
    /      /     -->     |      |
 p1/______/ p4        0,0|______|1,0
```

**compute\_warp\_square\_to\_quad(p1, p2, p3, p4)** - returns a matrix that maps the unit square to an arbitrary quadrilateral defined by points p1, p2, p3, and p4.

```
0,1 ______ 1,1         p2 _______ p3
   |      |              /      /
   |      |   -->       /      /
0,0|______|1,0       p1/______/ p4*
```

**compute\_warp\_quad\_to\_quad(quad1, quad2)** - returns a matrix that maps an arbitrary quadrilateral to another quadrilateral

```
   p2 _______ p3      q2 _______ q3
     /      /            \      \
    /      /     -->      \      \
 p1/______/ p4          q1 \______\ q4
```