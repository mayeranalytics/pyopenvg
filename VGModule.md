# Context Management #

As EGL support on non-mobile platforms is lacking, PyOpenVG depends on ShivaVG's createContextSH and destroyContextSH extensions to create an OpenVG context. These are exposed in VG.create\_context(dimensions) and VG.destroy\_context().

**create\_context(dimensions)**

Creates a OpenVG context with the supplied dimensions.

VG.create\_context(dimensions) must be called before instantiating any PyOpenVG instances (except for Context objects and Style objects, which are regular python objects) or calling any other VG or VGU functions.

**resize\_context(dimensions)**

Resizes the current OpenVG context.

**destroy\_context()**

Destroys the current OpenVG context.

## Getting/Setting Parameters ##

Context parameters (such as stroke width, dashing, scissoring, etc) are accessed through the get and set functions. These functions abstract away the details of remembering whether the parameter is a float or an int or how many parameters it's supposed to return.
However, for this reason it is not recommended that you use `from OpenVG.VG import *`. Doing so would shadow the builtin set type. If you must do so, use `from OpenVG import VG` and alias VG.get and VG.set to vgGet and vgSet.

**get(param\_type)**

Given a param from the VGParamType enumeration, this returns the corresponding context parameter. See the [specification and header file](http://khronos.org/openvg/) for a full list of context parameters, their behaviors, and default values.

Example:
```
color = VG.get(VG_CLEAR_COLOR)
```

**set(param\_type, value)**

Given a param from the VGParamType enumeration, this sets the corresponding context parameter to value.

Example:
```
VG.set(VG_STROKE_DASH_PATTERN, (5, 10))
```

## Getting/Setting Paint ##

In OpenVG, filling and stroking is abstracted into [Paint](PaintClass.md) objects, which represent a means of coloring a surface. Each paint object stores the information needed to paint a surface (color, gradient stops, etc). A paint mode can be associated with stroking, filling, or both.

**get\_paint(mode)**

VG.get\_paint(paint\_mode) returns the current paint set for mode (which must be either VG\_STROKE\_PATH or VG\_FILL\_PATH) or None if no paint has been set.

**set\_paint(paint, mode)**

VG.set\_paint(paint, mode) sets the paint for mode (which must be VG\_STROKE\_PATH, VG\_FILL\_PATH, or result of bitwise ORing them together) to paint. If paint is None, then the default paint is set (opaque black).

## Querying OpenVG properties ##

OpenVG exposes implementation-specific information such as the vendor, version, renderer, and extensions through the vgGetString function.

**get\_string(string\_id)**

VG.get\_string(string\_id) returns the corresponding string information. Valid values include VG\_VENDOR, VG\_RENDERER, VG\_VERSION, and VG\_EXTENSIONS. This may not be called before the context has been created.



# Graphics Functions #

**clear(corner, dimensions, color=None)**

VG.clear(corner, dimensions, color) clears the area from corner (the bottom left corner) with the dimensions supplied. If color is not None, then that RGBA 4-tuple is used as the clear color. Otherwise the screen is clear with VG\_CLEAR\_COLOR.

**flush()**

VG.flush() tells OpenVG to hurry up and complete all pending drawing requests, but does not guarantee that all pending requests will be completed.

**finish()**

VG.finish tells OpenVG to block until all pending drawing requests are complete.

# Transformations #

## Matrix manipulation ##

The matrix mode can be set using VG.set(VG\_MATRIX\_MODE, mode), where mode is from

```
typedef enum {
  VG_MATRIX_PATH_USER_TO_SURFACE              = 0x1400,
  VG_MATRIX_IMAGE_USER_TO_SURFACE             = 0x1401,
  VG_MATRIX_FILL_PAINT_TO_USER                = 0x1402,
  VG_MATRIX_STROKE_PAINT_TO_USER              = 0x1403
} VGMatrixMode;
```

**get\_matrix()**

VG.get\_matrix() returns the flattened 3x3 transformation matrix for the current matrix mode.

**load\_matrix(M)**

VG.load\_matrix(M) loads M (which must be 9 elements long; affine matrices must be padded) as the transformation matrix for the current matrix mode

**load\_identity()**

VG.load\_identity() loads the identity matrix as the transformation matrix for the current matrix mode.

**mult\_matrix(M)**

VG.mult\_matrix(M) multiplies the current transformation matrix by M.

## General Transformation Functions ##

**translate(tx, ty)**

VG.translate(tx, ty) translates the drawing surface by (tx, ty) pixels

**scale(sx, sy)**

VG.scale(sx, sy) scales the drawing surface time sx in the x direction and sy in the y direction

**rotate(angle)**

VG.rotate(angle) rotates the drawing surface by angle degrees

**shear(shx, shy)**

VG.shear(shx, shy) shears the drawing surface by shx, shy