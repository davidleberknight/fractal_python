# Abstract Class FractalCalculator
# Concrete subclasses for Mandlebrot and Julia Sets

from PyQt5 import QtCore, QtGui

class FractalCalculator():
    def __init__(self,newDrawing):
        self.drawing = newDrawing

    def calc_color(self,x,y,colorManager):
        delta  = (self.drawing.fractalRect.rMax - self.drawing.fractalRect.rMin) / self.drawing.width;
        zR = self.drawing.fractalRect.rMin + ( x ) * delta;
        zI = self.drawing.fractalRect.iMin + (( self.drawing.height - y )) * delta;
        numIterations = self.test_point( zR, zI, self.drawing.maxIterations);
        color = self.lookup_color( numIterations, self.drawing.maxIterations, colorManager )
        return color

    def lookup_color(self, numIters, maxIters, colorManager):
        if numIters != 0:
            colorNum = int(colorManager.numColors() * (1 -(numIters / maxIters)))
            if colorNum == colorManager.numColors():
                colorNum = 0
            color = colorManager.lookup(colorNum)
        else:
            color = (0, 0, 0)
        return color

    def plot_image(self, colorManager):
        for x in range(self.drawing.width):
            for y in range(self.drawing.height):
                color = self.calc_color(x,y,colorManager)
                self.drawing.image.setPixel(x, y, QtGui.qRgb(color[0], color[1], color[2]))

    def test_point(self, cR, cI, max_iter):
        pass

class MandlebrotCalculator(FractalCalculator):
    def test_point(self, cR, cI, maxIterations ):
        zR = cR
        zI = cI
        for i in range(1, maxIterations ):
            zROld = zR
            zR = zR * zR - zI * zI + cR
            zI = 2 * zROld * zI + cI
            distSquared = zR * zR + zI * zI
            if distSquared >= 4:
                return i
        return 0

class JuliaCalculator(FractalCalculator):
    def test_point(self, zR, zI, maxIterations ):
        for i in range(1, maxIterations ):
            zROld = zR
            zR = zR * zR - zI * zI + self.drawing.juliaPoint.real
            zI = 2 * zROld * zI + self.drawing.juliaPoint.imaginary
            distSquared = zR * zR + zI * zI
            if distSquared >= 4:
                return i
        return 0
        

