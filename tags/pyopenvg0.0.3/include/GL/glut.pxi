include "glu.pxi"
cdef extern from "GL/glut.h":
    void glutInit(int *argcp, char **argv)
##    void __glutInitWithExit(int *argcp, char **argv, void (__cdecl *exitfunc)(int))
##    cdef static void glutInit_ATEXIT_HACK(int *argcp, char **argv):
##        __glutInitWithExit(argcp, argv, exit)
##    DEF glutInit glutInit_ATEXIT_HACK

    void glutInitDisplayMode(unsigned int mode)
    
    void glutInitWindowPosition(int x, int y)
    void glutInitWindowSize(int width, int height)
    void glutMainLoop()
    
    int glutCreateWindow(char *title)
##    int __glutCreateWindowWithExit(char *title, void (__cdecl *exitfunc)(int))
##    cdef static int glutCreateWindow_ATEXIT_HACK(char *title):
##        return __glutCreateWindowWithExit(title, exit)
##    DEF glutCreateWindow glutCreateWindow_ATEXIT_HACK
    
    int glutCreateSubWindow(int win, int x, int y, int width, int height)
    void glutDestroyWindow(int win)
    void glutPostRedisplay()

    void glutSwapBuffers()
    int glutGetWindow()
    void glutSetWindow(int win)
    void glutSetWindowTitle(char *title)
    void glutSetIconTitle(char *title)
    void glutPositionWindow(int x, int y)
    void glutReshapeWindow(int width, int height)
    void glutPopWindow()
    void glutPushWindow()
    void glutIconifyWindow()
    void glutShowWindow()
    void glutHideWindow()

    void glutFullScreen()
    void glutSetCursor(int cursor)

    void glutEstablishOverlay()
    void glutRemoveOverlay()
    void glutUseLayer(GLenum layer)
    void glutPostOverlayRedisplay()

    void glutShowOverlay()
    void glutHideOverlay()

    int glutCreateMenu(void (*func)(int))
##    int __glutCreateMenuWithExit(void (__cdecl *func)(int), void (__cdecl *exitfunc)(int))
##    cdef static int glutCreateMenu_ATEXIT_HACK(void (__cdecl *func)(int)):
##        return __glutCreateMenuWithExit(func, exit)
##    DEF glutCreateMenu glutCreateMenu_ATEXIT_HACK

    void glutDestroyMenu(int menu)
    int glutGetMenu()
    void glutSetMenu(int menu)
    void glutAddMenuEntry(char *label, int value)
    void glutAddSubMenu(char *label, int submenu)
    void glutChangeToMenuEntry(int item, char *label, int value)
    void glutChangeToSubMenu(int item, char *label, int submenu)
    void glutRemoveMenuItem(int item)
    void glutAttachMenu(int button)
    void glutDetachMenu(int button)

    void glutDisplayFunc(void (*func)())
    void glutReshapeFunc(void (*func)(int width, int height))
    void glutKeyboardFunc(void (*func)(unsigned char key, int x, int y))
    void glutMouseFunc(void (*func)(int button, int state, int x, int y))
    void glutMotionFunc(void (*func)(int x, int y))
    void glutPassiveMotionFunc(void (*func)(int x, int y))
    void glutEntryFunc(void (*func)(int state))
    void glutVisibilityFunc(void (*func)(int state))
    void glutIdleFunc(void (*func)())
    void glutTimerFunc(unsigned int millis, void (*func)(int value), int value)
    void glutMenuStateFunc(void (*func)(int state))

    void glutSpecialFunc(void (*func)(int key, int x, int y))
    void glutSpaceballMotionFunc(void (*func)(int x, int y, int z))
    void glutSpaceballRotateFunc(void (*func)(int x, int y, int z))
    void glutSpaceballButtonFunc(void (*func)(int button, int state))
    void glutButtonBoxFunc(void (*func)(int button, int state))
    void glutDialsFunc(void (*func)(int dial, int value))
    void glutTabletMotionFunc(void (*func)(int x, int y))
    void glutTabletButtonFunc(void (*func)(int button, int state, int x, int y))

    void glutMenuStatusFunc(void (*func)(int status, int x, int y))
    void glutOverlayDisplayFunc(void (*func)())

    void glutSetColor(int, GLfloat red, GLfloat green, GLfloat blue)
    GLfloat glutGetColor(int ndx, int component)
    void glutCopyColormap(int win)

    int glutGet(GLenum type)
    int glutDeviceGet(GLenum type)

    int glutExtensionSupported(char *name)
    
    int glutGetModifiers()
    int glutLayerGet(GLenum type)

    void glutBitmapCharacter(void *font, int character)
    int glutBitmapWidth(void *font, int character)
    void glutStrokeCharacter(void *font, int character)
    int glutStrokeWidth(void *font, int character)

    void glutWireSphere(GLdouble radius, GLint slices, GLint stacks)
    void glutSolidSphere(GLdouble radius, GLint slices, GLint stacks)
    void glutWireCone(GLdouble base, GLdouble height, GLint slices, GLint stacks)
    void glutSolidCone(GLdouble base, GLdouble height, GLint slices, GLint stacks)
    void glutWireCube(GLdouble size)
    void glutSolidCube(GLdouble size)
    void glutWireTorus(GLdouble innerRadius, GLdouble outerRadius, GLint sides, GLint rings)
    void glutSolidTorus(GLdouble innerRadius, GLdouble outerRadius, GLint sides, GLint rings)
    void glutWireDodecahedron()
    void glutSolidDodecahedron()
    void glutWireTeapot(GLdouble size)
    void glutSolidTeapot(GLdouble size)
    void glutWireOctahedron()
    void glutSolidOctahedron()
    void glutWireTetrahedron()
    void glutSolidTetrahedron()
    void glutWireIcosahedron()
    void glutSolidIcosahedron()

# Constants
GLUT_RGB = GLUT_RGBA = 0
GLUT_INDEX = 1
GLUT_SINGLE = 0
GLUT_DOUBLE = 2
GLUT_ACCUM = 4
GLUT_ALPHA = 8
GLUT_DEPTH = 16
GLUT_STENCIL = 32
GLUT_MULTISAMPLE =128
GLUT_STEREO = 256
GLUT_LUMINANCE = 512

GLUT_LEFT_BUTTON = 0
GLUT_MIDDLE_BUTTON = 1
GLUT_RIGHT_BUTTON = 2

GLUT_DOWN = 0
GLUT_UP = 1

GLUT_KEY_F1 = 1
GLUT_KEY_F2 = 2
GLUT_KEY_F3 = 3
GLUT_KEY_F4 = 4
GLUT_KEY_F5 = 5
GLUT_KEY_F6 = 6
GLUT_KEY_F7 = 7
GLUT_KEY_F8 = 8
GLUT_KEY_F9 = 9
GLUT_KEY_F10 = 10
GLUT_KEY_F11 = 11
GLUT_KEY_F12 = 12

GLUT_KEY_LEFT = 100
GLUT_KEY_UP = 101
GLUT_KEY_RIGHT = 102
GLUT_KEY_DOWN = 103
GLUT_KEY_PAGE_UP = 104
GLUT_KEY_PAGE_DOWN = 105
GLUT_KEY_HOME = 106
GLUT_KEY_END = 107
GLUT_KEY_INSERT = 108

GLUT_LEFT = 0
GLUT_ENTERED = 1

GLUT_MENU_NOT_IN_USE = 0
GLUT_MENU_IN_USE = 1

GLUT_NOT_VISIBLE = 0
GLUT_VISIBLE = 1

GLUT_HIDDEN = 0
GLUT_FULLY_RETAINED = 1
GLUT_PARTIALLY_RETAINED = 2
GLUT_FULLY_COVERED = 3

GLUT_RED = 0
GLUT_GREEN = 1
GLUT_BLUE = 2

GLUT_WINDOW_X = (<GLenum> 100)
GLUT_WINDOW_Y = (<GLenum> 101)
GLUT_WINDOW_WIDTH = (<GLenum> 102)
GLUT_WINDOW_HEIGHT = (<GLenum> 103)
GLUT_WINDOW_BUFFER_SIZE = (<GLenum> 104)
GLUT_WINDOW_STENCIL_SIZE = (<GLenum> 105)
GLUT_WINDOW_DEPTH_SIZE = (<GLenum> 106)
GLUT_WINDOW_RED_SIZE = (<GLenum> 107)
GLUT_WINDOW_GREEN_SIZE = (<GLenum> 108)
GLUT_WINDOW_BLUE_SIZE = (<GLenum> 109)
GLUT_WINDOW_ALPHA_SIZE = (<GLenum> 110)
GLUT_WINDOW_ACCUM_RED_SIZE = (<GLenum> 111)
GLUT_WINDOW_ACCUM_GREEN_SIZE = (<GLenum> 112)
GLUT_WINDOW_ACCUM_BLUE_SIZE = (<GLenum> 113)
GLUT_WINDOW_ACCUM_ALPHA_SIZE = (<GLenum> 114)
GLUT_WINDOW_DOUBLEBUFFER = (<GLenum> 115)
GLUT_WINDOW_RGBA = (<GLenum> 116)
GLUT_WINDOW_PARENT = (<GLenum> 117)
GLUT_WINDOW_NUM_CHILDREN = (<GLenum> 118)
GLUT_WINDOW_COLORMAP_SIZE = (<GLenum> 119)
GLUT_WINDOW_NUM_SAMPLES = (<GLenum> 120)
GLUT_WINDOW_STEREO = (<GLenum> 121)
GLUT_WINDOW_CURSOR = (<GLenum> 122)
GLUT_SCREEN_WIDTH = (<GLenum> 200)
GLUT_SCREEN_HEIGHT = (<GLenum> 201)
GLUT_SCREEN_WIDTH_MM = (<GLenum> 202)
GLUT_SCREEN_HEIGHT_MM = (<GLenum> 203)
GLUT_MENU_NUM_ITEMS = (<GLenum> 300)
GLUT_DISPLAY_MODE_POSSIBLE = (<GLenum> 400)
GLUT_INIT_WINDOW_X = (<GLenum> 500)
GLUT_INIT_WINDOW_Y = (<GLenum> 501)
GLUT_INIT_WINDOW_WIDTH = (<GLenum> 502)
GLUT_INIT_WINDOW_HEIGHT = (<GLenum> 503)
GLUT_INIT_DISPLAY_MODE = (<GLenum> 504)
GLUT_ELAPSED_TIME = (<GLenum> 700)

GLUT_HAS_KEYBOARD = (<GLenum> 600)
GLUT_HAS_MOUSE = (<GLenum> 601)
GLUT_HAS_SPACEBALL = (<GLenum> 602)
GLUT_HAS_DIAL_AND_BUTTON_BOX = (<GLenum> 603)
GLUT_HAS_TABLET = (<GLenum> 604)
GLUT_NUM_MOUSE_BUTTONS = (<GLenum> 605)
GLUT_NUM_SPACEBALL_BUTTONS = (<GLenum> 606)
GLUT_NUM_BUTTON_BOX_BUTTONS = (<GLenum> 607)
GLUT_NUM_DIALS = (<GLenum> 608)
GLUT_NUM_TABLET_BUTTONS = (<GLenum> 609)

GLUT_OVERLAY_POSSIBLE = (<GLenum> 800)
GLUT_LAYER_IN_USE = (<GLenum> 801)
GLUT_HAS_OVERLAY = (<GLenum> 802)
GLUT_TRANSPARENT_INDEX = (<GLenum> 803)
GLUT_NORMAL_DAMAGED = (<GLenum> 804)
GLUT_OVERLAY_DAMAGED = (<GLenum> 805)

GLUT_NORMAL = (<GLenum> 0)
GLUT_OVERLAY = (<GLenum> 1)

GLUT_ACTIVE_SHIFT = 1
GLUT_ACTIVE_CTRL = 2
GLUT_ACTIVE_ALT = 4

GLUT_CURSOR_RIGHT_ARROW = 0
GLUT_CURSOR_LEFT_ARROW = 1

GLUT_CURSOR_INFO = 2
GLUT_CURSOR_DESTROY = 3
GLUT_CURSOR_HELP = 4
GLUT_CURSOR_CYCLE = 5
GLUT_CURSOR_SPRAY = 6
GLUT_CURSOR_WAIT = 7
GLUT_CURSOR_TEXT = 8
GLUT_CURSOR_CROSSHAIR = 9

GLUT_CURSOR_UP_DOWN = 10
GLUT_CURSOR_LEFT_RIGHT = 11

GLUT_CURSOR_TOP_SIDE = 12
GLUT_CURSOR_BOTTOM_SIDE = 13
GLUT_CURSOR_LEFT_SIDE = 14
GLUT_CURSOR_RIGHT_SIDE = 15
GLUT_CURSOR_TOP_LEFT_CORNER = 16
GLUT_CURSOR_TOP_RIGHT_CORNER = 17
GLUT_CURSOR_BOTTOM_RIGHT_CORNER = 18
GLUT_CURSOR_BOTTOM_LEFT_CORNER = 19

GLUT_CURSOR_INHERIT = 100

GLUT_CURSOR_NONE = 101

GLUT_CURSOR_FULL_CROSSHAIR = 102


