# Introduction #

The Path class wraps a VGPath handle and provides the functionality needed to create, transform, and draw paths.

Note: Path objects have a style attribute which can be used to automatically set the corresponding context parameters when drawing and then restore the old parameters.

# Properties #
  * **format** - The path format used by OpenVG. Normally this is 0.

  * **datatype** - The datatype that path coordinates are stored as. Usually this will be VG\_PATH\_DATATYPE\_F.

  * **scale** - The scaling factor applied to all incoming path coordinates

  * **bias** - The bias (offset) applied to all incoming path coordinates

  * **num\_segments** - The number of segments in the path

  * **num\_coords** - The number of coordinates that define the path

  * **capabilities** - The bitwise OR of the capabilities supported by the path. Normally VG\_PATH\_CAPABILITY\_ALL.

Capabilities can be removed by using "path.capabilities &= ~(capability1 | capability2 | capability3)"

Example:
```
path.capabilities &= ~(VG_PATH_CAPABILITY_TRANSFORM_TO | VG_PATH_CAPBILITY_TRANSFORM_FROM)
```

# Methods #
**`__`init`__`(format=0, datatype=VG\_PATH\_DATATYPE\_F, scale=1.0, bias=0, segment\_hint=0, coord\_hint=0, capabilities=VG\_PATH\_CAPABILITY\_ALL)**

For the most part, there is no reason to pass the constructor any values besides the defaults.
  * format corresponds to the path format used internally by OpenVG. 0 indicates the standard format currently.
  * datatype is a constant indicating the datatype used to represent the path coordinates. Other options are VG\_PATH\_DATATYPE\_S\_8, VG\_PATH\_DATATYPE\_S\_16, and VG\_PATH\_DATATYPE\_32. Certain kinds of paths (such as fonts) fit nicely in smaller datatypes.
  * segment and bias are used together with the datatype to define the valid range of coordinates. A given coordinate v is mapped to v\*scale + bias.
  * segment\_hint and coord\_hint are hints to OpenVG telling it how much space it might need to allocate for a given path. Setting these might help performance a little, but probably won't make a difference.
  * capabilities is a bitwise OR of the various capabilities that paths have (such has appending data, transforming, interpolating, etc). In theory OpenVG can save space if you specify fewer capabilities, but most of the time you'll want to stick with VG\_PATH\_CAPABILITY\_ALL.

**clear(capabilities=None)**

Path.clear(capabilities) will empty the path, removing all segments. Additionally, the handle will refer to a path with the specified capabilities (which default to the old path's capabilities if None is passed) and the same datatype and format. This may be faster than creating and destroying many short-lived paths of the same format.

**append(segment)**

Path.append(segment) appends a single path segment to the path. segment must be of the form (command, data) where command is one of the OpenVG path commands and data is a tuple of the corresponding control points.

Example:
```
path = VG.Path()
path.append((VG_MOVE_TO_ABS, (10.0, 10.0)))
```

**extend(segments)**

Path.extend(segments) works just like you would expect list.extend to. It takes either a list of segments formatted like with Path.append or another path and it adds the segments to the path.

Example:
```
path = VG.Path()
segments = [(VG_MOVE_TO_ABS, ( 10.0, 10.0)),
            (VG_LINE_TO_REL, (  0.0, 20.0)),
            (VG_LINE_TO_REL, ( 20.0,  0.0)),
            (VG_LINE_TO_REL, (-10.0,  0.0)),
            (VG_CLOSE_PATH, ())]
path.extend(segments)
```

**modify(index, data)**

Path.modify(index, data) sets the segment data for segments starting at index to data

Example:
```
#Create a path, then translate it and grow it
path = VG.Path()
segments = [(VG_MOVE_TO_ABS, ( 10.0, 10.0)),
            (VG_LINE_TO_REL, (  0.0, 20.0)),
            (VG_LINE_TO_REL, ( 20.0,  0.0)),
            (VG_LINE_TO_REL, (-20.0,  0.0)),
            (VG_CLOSE_PATH, ())]
path.extend(segments)

#This changes the initial VG_MOVE_TO_ABS to 100.0,100.0 instead of 10.0,10.0
path.modify(0, [(100.0, 100.0)])
#This changes the VG_LINE_TO_RELs to move further
path.modify(1, [(  0.0, 50.0),
                ( 50.0,  0.0),
                (-50.0,  0.0)])
```

**transform(dest=None)**

Path.transform(dest) appends a version of the path with the segments transformed by the current matrix to dest. If dest is None, then a new path is created and returned with the transformed segments. This does **not** modify the original path.

Example:
```
#Translate to the center, then rotate 60 degrees, then create a copy of the path with
#this transformation applied
VG.translate(320, 240)
VG.rotate(60)
path = path.transform()
```

**get\_point(distance, start=0, num\_segments=None)**

Path.get\_point(distance, start, num\_segments) returns the point and its tangent vector that one would get by starting at the end point of the path segment start and moving along the subpath defined by the next num\_segments segments (or the entire path if None) and travelling distance units.

**length(start=0, num\_segments=None**

Path.length(start, num\_segments) returns the length of the subpath starting with the start-th segment and ending num\_segments later (or the rest of the path if None). Path.length() with no arguments will return the length of the entire path.

**draw(paint\_modes, style=None)**

Path.draw(paint\_modes, style) draws the path to the screen.
  * paint\_modes is the bitwise OR of VG\_FILL\_PATH or VG\_STROKE\_PATH. If paint\_modes is VG\_FILL\_PATH, only the fill will be drawn. If paint\_modes is VG\_STROKE\_PATH then only the stroke will be drawn. If paint\_modes is VG\_FILL\_PATH | VG\_STROKE\_PATH, then both will be drawn.
  * style is an optional argument, which if supplied stores the style information that the path will use to draw path. It will be combined with the path's style object if any. It should be an instance of the [VG.Style](StyleClass.md) class or a subclass.

The following methods simply append the corresponding segment command to the path:
  * **move\_to(p, rel=False)** - moves the path to point p
  * **line\_to(p, rel=False)** - draws a line to point p
  * **hline\_to(x, rel=False)** - draws a horizontal line to x
  * **vline\_to(y, rel=False)** - draws a vertical line to y
  * **quad\_to(p1, p2, rel=False)** - draws a quadratic Bezier curve to p2 with control point p1
  * **squad\_to(p2, rel=False)** - draws a smooth quadratic Bezier curve to p2 using the reflection of the previous control point across the previous end point as the control point
  * **cubic\_to(p1, p2, p3, rel=False)** - draws a cubic Bezier curve to p3 with control points p1 and p2
  * **scubic\_to(p2, p3, rel=False)** - draws a smooth cubic Bezier curve to p3 with control point p2 and the reflection of the previous control point across the previous end point.
  * **arc\_to(p1, rh, rv, rot, major, CCW, rel=False)** - draws an elliptical arc passing through p1. major determines if it is a large or small arc. See section _8.4 Elliptical Arcs_ of the OpenVG specification for more details.
> > New in 0.0.4: The CW argument has been switched to CCW.
  * **close()** - closes the current subpath (a line will be drawn to the beginning of the subpath if stroked)


# Other functions #
**interpolate(start, end, dest, amount)**

VG.interpolate(start, end, dest, amount) appends the result of interpolating or extrapolating (if amount is outside of [0.0,1.0]) amount between start and end. If dest is None, a new path will be created with the interpolated path segments appended. In order for two paths to be interpolated, they must have the exact same series of commands.
See the [Interpolation example](http://code.google.com/p/pyopenvg/source/browse/trunk/examples/vg_pygame_interpolate.py) to see an example of how to do interpolation.