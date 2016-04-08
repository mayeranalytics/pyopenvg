# Introduction #

In OpenVG, VGPaint objects determine how paths are stroked and filled. A given paint object has many parameters, but only those relevant to the type of paint are used (VG\_PAINT\_COLOR is only applicable to paint objects of type VG\_PAINT\_TYPE\_COLOR). Instead of having one monolithic paint class which allows the user to set parameters that are not used by the type of paint, subclasses of the base Paint class implement the functionality relevant to each paint type: ColorPaint handles solid colors, GradientPaint handles radial and linear gradients of color, and PatternPaint handles patterns based on images.

## Common Properties ##
These properties are common to all paint classes.
  * **transform** - an OpenVG transformation matrix that specifies the appropriate paint transformation when used with a style. None by default.


# ColorPaint #

## Properties ##
  * **color** - a 4-tuple representing the color.

The simplest of the paint types, ColorPaint represents a solid color such as red or blue. It takes a single parameter, color which can be a 3-tuple of colors in the RGB format (from 0.0 to 1.0) or a 4-tuple of the colors and alpha.

Example:
```
#Make the stroke paint red and the fill paint translucent green
red = VG.ColorPaint((1.0, 0.0, 0.0))
translucent_green = VG.ColorPaint((0.0, 1.0, 0.0, 0.5))
VG.set_paint(red, VG_STROKE_PATH)
VG.set_paint(translucent_green, VG_FILL_PATH)
```

# GradientPaint #

## Properties ##
  * **gradient** - For linear gradients, this is a pair of tuples representing the start and end points in the form (start, end). For radial gradients, this is a pair of tuples and the radius representing the center and focus points in the form (center, focus, radius).
  * **stops** - a list of the color ramp stops that define the gradient colors.
  * **spread\_mode** - the mode that OpenVG uses to determine the colors for points outside of the gradient.
  * **opacity** - a float from 0.0 to 1.0 which will be multiplied with the stop-colors' opacities.

The GradientPaint class can represent either a linear or radial gradient. Both radial and linear gradients consist of two parts: the gradient function which maps a given coordinate to a value in the range [0, 1] and a color ramp, which maps colors to each value in the range [0, 1]. For more information on how the gradient function for linear and radial gradients are defined, see the [OpenVG specs](http://www.khronos.org/openvg/).

Each color stop consists of a tuple of the form (offset, color). For any given point on the color ramp, the color is determined by linearly interpolating between the two nearest color stops. Outside of the range [0, 1] the color is determined by the spread mode, which can be one of the following:
  * **VG\_COLOR\_RAMP\_SPREAD\_PAD** - this is the default spread mode. Anything outside is simply mapped to the same color as the start or end stop - anything greater than 1 is the same color as the end of the gradient and anything less than 0 is the same color as the beginning of the gradient.
  * **VG\_COLOR\_RAMP\_SPREAD\_REPEAT** - The gradient function starts over again as if it had a period of 1.
  * **VG\_COLOR\_RAMP\_SPREAD\_REFLECT** - The gradient function is reflected across either 0 or 1, depending on if number is less than 0 or greater than 1, respectively.

Example:
```
#Create a linear gradient going from white to red to green to blue
paint = VG.GradientPaint([(0,0), (250,0)], linear=True)
   
#Set the color stops
paint.stops = [(0.0,  (0.0, 0.0, 0.0, 1.0)), #white
               (0.333,(1.0, 0.0, 0.0, 1.0)), #red
               (0.666,(0.0, 1.0, 0.0, 1.0)), #green
               (1.0,  (0.0, 0.0, 1.0, 1.0))] #blue

#Set the spread mode to reflect because it's prettier
paint.spread_mode = VG_COLOR_RAMP_SPREAD_REFLECT
```
If drawn on a 250x100 rectangle, this would result in:
> ![http://chart.apis.google.com/chart?chs=250x100&chf=bg,lg,0,ffffff,0,ff0000,0.333,00ff00,0.666,0000ff,1&cht=bhs&ftype=chart.png](http://chart.apis.google.com/chart?chs=250x100&chf=bg,lg,0,ffffff,0,ff0000,0.333,00ff00,0.666,0000ff,1&cht=bhs&ftype=chart.png)

Example:
```
#Create a simple radial gradient going with center == focus
paint = VG.GradientPaint([(50,50), (50,50), 50], linear=False)

#Set the color stops
paint.stops = [(0.0,  (0.0, 0.0, 0.0, 1.0)), #white
               (0.333,(1.0, 0.0, 0.0, 1.0)), #red
               (0.666,(0.0, 1.0, 0.0, 1.0)), #green
               (1.0,  (0.0, 0.0, 1.0, 1.0))] #blue
```
# PatternPaint #
## Properties ##
  * **pattern** - the image being used as a pattern.
PatternPaint is not yet fully supported as the Image support is not yet complete.