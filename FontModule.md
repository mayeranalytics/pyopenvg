# Introduction #

Because OpenVG 1.0 does not specify any methods for font rendering, it is necessary to use third-party libraries to handle text. OpenVG.font uses a minimal wrapper around FreeType2 (internally called FT, if you really want to get at it) to read in the outline data for outline fonts such as TrueType. The glyph data is read and used to create short paths for each glyph which are then placed according to individual font metrics and kerning rules to render a block of text as a path.

This is not as fast as it would be to simply use FreeType to render the text to a bitmap and then draw that to the screen directly, but allows for more flexibility (And I have not yet gotten around to writing the wrappers around the glyph rendering part of FreeType).

A short example:

```
import OpenVG.font
vera = OpenVG.font.Font("data/Vera.ttf", 14)

message = vera.build_path("Hello, world!")
message.draw(VG_FILL_PATH)
```

# The Font Class #

The font module exposes a single class that has the functionality that you need to render text: the Font class.

## Attributes ##

You really shouldn't need to access any attributes directly, but in case you need to do some introspection:

  * **path** - the path which was passed to the constructor to load the font from
  * **size** - the size of the font in points (1/72 of an inch)
  * **face** - the internal FreeType face object wrapper.
  * **glyph\_table** - a dictionary mapping character codes (`ord(s)`) to glyph wrappers
  * **path\_table** - a dictionary mapping glyph indices to paths

## Methods ##

**`__`init`__`(path, size, dpi=72, preload=True)** - creates a new Font object from the font face located at path with the given size in pts at the specified dpi. If preload is True, then all glyphs will be loaded immediately.

**build\_path(text, horizontal=True, do\_kerning=True)** - creates a path for a given string of text. If horizontal is false, then the text will be aligned vertically. Kerning is the adjustment of spacing between certain letter pairs to make them look better. Kerning is mutually exclusive with vertical text.

**compile\_paths()** - loads all glyphs immediately

**get\_path\_for\_char(char)** - loads (if necessary) the appropriate glyph for char and returns the associated path.