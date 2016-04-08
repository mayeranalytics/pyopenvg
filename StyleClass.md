# Introduction #

Style objects take care of storing, setting, and restoring the OpenVG context parameters related to styling and drawing. For example, this code:

```
#Save old settings
old_paint = VG.get_paint(VG_STROKE_PATH)
old_stroke_width = VG.get(VG_STROKE_LINE_WIDTH)

#Set current settings
VG.set_paint(stroke_paint, VG_STROKE_PATH)
VG.set(VG_STROKE_LINE_WIDTH, 5.0)
    
#Draw
path.draw(VG_STROKE_PATH)

#Restore old settings
VG.set_paint(old_paint, VG_STROKE_PATH)
VG.set(VG_STROKE_LINE_WIDTH, old_stroke_width)
```

becomes

```
#Create style object
style = VG.Style(stroke_paint=stroke_paint, VG_STROKE_LINE_WIDTH=5.0)
    
#Set current settings
style.enable()
    
#Draw
path.draw(VG_STROKE_PATH)

#Restore old settings
style.disable()
```
Style objects are also context managers, allowing you to use the with statement introduced in Python 2.6:

```
style = VG.Style(stroke_paint=stroke_paint, VG_STROKE_LINE_WIDTH=5.0)
with style:
    path.draw(VG_STROKE_PATH)
```
For one-off things, you can also pass a style parameter to path.draw

```
style = VG.Style(stroke_paint=stroke_paint, VG_STROKE_LINE_WIDTH=5.0)
path.draw(VG_STROKE_PATH, style=style)
```

# Getting and setting style parameters #

You can get or set any style parameter (such as VG\_STROKE\_DASH\_PATTERN) by using style[VG\_STROKE\_DASH\_PATTERN](VG_STROKE_DASH_PATTERN.md). The only exception is that paint must be accessed directly through style.stroke\_paint and style.fill\_paint.

Example:
```
style = VG.Style(stroke_paint=VG.ColorPaint((1.0, 0.0, 0.0)), #red stroke paint
                 VG_STROKE_DASH_PATTERN = (5, 10))            #dash pattern of 5 on, 10 off
print style[VG_STROKE_DASH_PATTERN] #should print (5, 10)
    
#Set the fill paint to purple
style.fill_paint = VG.ColorPaint((1.0, 0.0, 1.0)) 
```


# Caveats #

Although get\_paint and set\_paint usually use None to signify that the default paint is being used or set, Style objects will **not** set the paint to the default if None is passed in.