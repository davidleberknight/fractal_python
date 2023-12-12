# ColorManager for Fractal Application
# AND OTHER HELPER CLASSES
import colorsys

NUM_COLORS = 120
COLORS_CLASSIC = "CLASSIC"
COLORS_FOREST = "FOREST"
COLORS_PASTEL = "PASTEL"
# TO DO: add more color maps
INITIAL_COLORMAP = "FOREST"

class ComplexPoint():
    def __init__(self,r,i):
        self.real=r
        self.imaginary=i

class ComplexRectangle():
    def __init__(self,rmax,rmin,imax,imin):
        self.rMax=rmax
        self.rMin=rmin
        self.iMax=imax
        self.iMin=imin

class PixelPoint():
    def __init__(self,_x,_y):
        self.x = _x
        self.y = _y

class PixelRectangle():
    def __init__(self,x_ul,y_ul,w,h):
        self.xUL = x_ul
        self.yUL = y_ul
        self.width = w
        self.height = h

class Drawing():
    def __init__(self,newImage,complexRect,w,h,maxIters,colorMap):
        self.image = newImage
        self.fractalRect = complexRect
        self.zoomRect = None 
        self.width = w
        self.height = h
        self.maxIterations = maxIters
        self.cmName = colorMap

    def set_zoom(self,pixelRect):
        self.zoomRect = pixelRect
        
class JuliaDrawing(Drawing):
    def __init__(self,newImage,complexRect,w,h,maxIters,colorMap,jp):
        super().__init__(newImage,complexRect,w,h,maxIters,colorMap)
        self.juliaPoint = jp

class Stack:
    def __init__(self):
        self.items = []

    def push(self, element):
        return self.items.append(element)

    def pop(self):
        if self.items:
            return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

class ColorManager():
    def __init__(self):
        self.cmTable = {}
        self.currentCM = INITIAL_COLORMAP

        # CLASSIC
        colorMap = {}
        for colorNum in range(NUM_COLORS-1, -1, -1):
            hue = (((colorNum * 2) % NUM_COLORS) / NUM_COLORS)
            saturation = (((colorNum * 2) % NUM_COLORS) / NUM_COLORS)
            brightness = 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, saturation, brightness)
            color = (int(red * 255), int(green * 255), int(blue * 255))      
            colorMap[colorNum] = color
        self.cmTable[COLORS_CLASSIC] = colorMap
      
        # FOREST
        colorMap = {}
        for colorNum in range(NUM_COLORS-1, -1, -1):
            red = ((1024 * colorNum / NUM_COLORS)) % 255
            green = ((256 * colorNum / NUM_COLORS)) % 255
            blue = ((512 * colorNum / NUM_COLORS)) % 255
            color = int(red),int(green), int(blue)
            colorMap[colorNum] = color
        self.cmTable[COLORS_FOREST] = colorMap

        # PASTEL
        colorMap = {}
        for colorNum in range(NUM_COLORS-1, -1, -1):
            hue = (((colorNum * 4) % NUM_COLORS) / NUM_COLORS)
            saturation = (((colorNum * 2) % NUM_COLORS) / NUM_COLORS)
            brightness = 1.0
            red, green, blue = colorsys.hsv_to_rgb(hue, saturation, brightness)
            color = (int(red * 255), int(green * 255), int(blue * 255))      
            colorMap[colorNum] = color
        self.cmTable[COLORS_PASTEL] = colorMap

    def initialColorMap(self):
        return INITIAL_COLORMAP

    def listOfColorMaps(self):
        return [COLORS_CLASSIC,COLORS_FOREST,COLORS_PASTEL]

    def lookup(self, colorNum):
        colorMap = self.cmTable[self.currentCM]
        return colorMap[colorNum]

    def numColors(self):
        return NUM_COLORS 

    def setCM(self, cmName):
        self.currentCM = cmName
