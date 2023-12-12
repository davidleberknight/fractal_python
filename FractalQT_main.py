### FRACTAL APPLICATION - MAIN
import sys
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from FractalCalculator import MandlebrotCalculator
from FractalCalculator import JuliaCalculator
from ColorManager import *

WIDTH = 600
HEIGHT = 600
INITIAL_ITERATIONS = 20
MANDLEBROT = "Mandlebrot"
JULIA = "Julia"
INITIAL_MANDLEBROT_RECTANGLE = ComplexRectangle( 1.5, -2.5, 2.0, -2.0 )
INITIAL_JULIA_RECTANGLE = ComplexRectangle( 2.0, -2.0, 2.0, -2.0 )

# FractalCanvas is A necessary subclass of QWidget
# this implements paintEvent for drawing, also handles the mouse events
class FractalCanvas(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.image = None
        self.fractalApp = parent

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)

    def set_image(self, image):
        self.image = image
        # Redraw the canvas
        self.update()

    def mouseMoveEvent(self, event):
        # Get the mouse position
        x = event.x()
        y = event.y()
        self.fractalApp.mouse_moved_event(x,y)

    def mouseReleaseEvent(self, event):
        self.fractalApp.mouse_up_event()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        self.fractalApp.mouse_down_event(x,y)

#########################################################################
class FractalApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.juliaSelectMode = False  
        self.zoomClick = PixelPoint(0,0) # Down click for zoom 
        self.mouseDown = False
        self.colorManager = ColorManager()
        self.firstPaint = True
        self.nextStack = Stack()
        self.previousStack = Stack()
        self.juliaPoint = ComplexPoint(0,0)
        self.previousIterations = INITIAL_ITERATIONS

        # Layout H1 :
        fractal_button = QtWidgets.QPushButton("Make New Fractal")
        fractal_button.clicked.connect(self.on_fractal_button_click)
        self.cm_list = QtWidgets.QComboBox()
        self.cm_list.addItems(self.colorManager.listOfColorMaps())
        self.cm_list.setCurrentText(self.colorManager.initialColorMap())
        self.cm_list.currentTextChanged.connect(self.on_color_map_change)
        H1_layout = QtWidgets.QHBoxLayout()
        H1_layout.addWidget(fractal_button) 
        H1_layout.addWidget(self.cm_list)

        # Layout H2 :
        H2_layout = QtWidgets.QHBoxLayout()
        self.next_button = QtWidgets.QPushButton("Next")
        self.next_button.clicked.connect(self.on_next_button_click)
        self.previous_button = QtWidgets.QPushButton("Previous")
        self.previous_button.clicked.connect(self.on_previous_button_click)
        self.delete_button = QtWidgets.QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete_button_click)
        H2_layout.addWidget(self.next_button)
        H2_layout.addWidget(self.previous_button)
        H2_layout.addWidget(self.delete_button)      
        self.next_button.setEnabled(False)
        self.previous_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        # Layout H3 :
        H3_layout = QtWidgets.QHBoxLayout()
        iterations_label = QtWidgets.QLabel("Max Iterations:")
        self.iterations_txt = QtWidgets.QLineEdit()
        self.iterations_txt.setText(str(INITIAL_ITERATIONS))
        H3_layout.addWidget(iterations_label)
        H3_layout.addWidget(self.iterations_txt)

        # Layour H4
        H4_layout = QtWidgets.QHBoxLayout()
        self.mj_list = QtWidgets.QComboBox()
        self.mj_list.addItems([MANDLEBROT,JULIA])
        self.mj_list.setCurrentText(MANDLEBROT)
        self.mj_list.currentTextChanged.connect(self.on_mj_change)
        jp_label = QtWidgets.QLabel("Julia Point:")
        self.jp_txt = QtWidgets.QLineEdit("Not Selected")
        H4_layout.addWidget(self.mj_list)
        H4_layout.addWidget(jp_label)
        H4_layout.addWidget(self.jp_txt)

        # Class FractalCanvas is required because Qlabel doesn't handle mouse events
        self.canvas = FractalCanvas(self)

        # Vertical layout - add H* sub-layouts and the canvas
        V_layout = QtWidgets.QVBoxLayout()
        V_layout.addLayout(H1_layout)
        V_layout.addLayout(H2_layout)
        V_layout.addLayout(H3_layout)
        V_layout.addLayout(H4_layout)
        V_layout.addWidget(self.canvas)

        # Set the layout to the central widget
        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(V_layout)
        self.setCentralWidget(central_widget)
        # The following is a hack to size the main window
        # A better way would be for the layout manager to autosize this
        # but I couldn't get it to work (canvas stubbornly drawn to zero size)
        self.setGeometry(0, 0, WIDTH+20, HEIGHT+135)

        # Draw the Hello World Fractal
        image = QtGui.QImage(WIDTH, HEIGHT, QtGui.QImage.Format_RGB888)
        newDrawing = Drawing(image, INITIAL_MANDLEBROT_RECTANGLE, WIDTH, HEIGHT, INITIAL_ITERATIONS, INITIAL_COLORMAP)
        self.do_make_new_fractal(newDrawing)
        self.show()
	
    ### FRACTAL APP CONTROLLER METHODS :
    def calculate_julia_point(self, pos):
        currentRect = self.currentDrawing.fractalRect
        delta = (currentRect.rMax - currentRect.rMin) / WIDTH
        jr = currentRect.rMin + (pos.x * delta)
        ji = currentRect.iMin + ((HEIGHT - pos.y)*delta)
        return ComplexPoint(jr,ji)

    def determine_max_iterations(self,complexRect):
        # If the user did not change the number of iterations, make a guess...
        maxIterations = self.currentDrawing.maxIterations
        try:
            maxIterations = int( self.iterations_txt.text())
        except ValueError:
            print("Max Iterations is not an integer")
            maxIterations = self.currentDrawing.maxIterations
        if self.previousIterations == maxIterations:
            initialWidth = INITIAL_MANDLEBROT_RECTANGLE.rMax - INITIAL_MANDLEBROT_RECTANGLE.rMin
            newWidth = complexRect.rMax - complexRect.rMin
            zoomFactor = initialWidth / newWidth
            if zoomFactor < 1:
                zoomFactor = 1
            logZoom = math.log(zoomFactor)
            magnitude = (logZoom/2.3)-2.0 # just a guess
            if magnitude < 1.0:
                magnitude = 1.0
            maxIterations = INITIAL_ITERATIONS * (magnitude * logZoom + 1.0)
        return maxIterations

    def display_julia_point(self,jp):
        # To Do: make this precision a variable, as with javascript version
        # use 5 decimal points for now
        roundedReal = "{:.5f}".format(jp.real)
        roundedImaginary = "{:.5f}".format(jp.imaginary)
        jpAsString = str(roundedReal)+","+str(roundedImaginary)
        self.jp_txt.setText(jpAsString )

    def do_delete_fractal(self):
        if self.nextStack.is_empty() and self.previousStack.is_empty():
            return
        if not self.nextStack.is_empty():
            self.currentDrawing = self.nextStack.pop()
        else:    
            self.currentDrawing = self.previousStack.pop()     
        self.update_control_panel()

    def do_make_new_fractal(self,newDrawing):
        if isinstance(newDrawing, JuliaDrawing):
            self.calculator = JuliaCalculator(newDrawing) 
        else:
            self.calculator = MandlebrotCalculator(newDrawing)

        self.calculator.plot_image(self.colorManager)
        self.canvas.set_image(newDrawing.image)

        if self.firstPaint == False:
            self.previousStack.push(self.currentDrawing)
            self.previous_button.setEnabled(True)
        else:
           self.firstPaint = False 
        self.currentDrawing = newDrawing;
        self.previousIterations = newDrawing.maxIterations
        self.update_control_panel()

    def do_next_fractal(self):
        if not self.nextStack.is_empty():
            self.do_next_previous(self.nextStack, self.previousStack)

    def do_next_previous(self, fromStack, toStack):
        toStack.push(self.currentDrawing)
        newCurrentDrawing = fromStack.pop()
        self.currentDrawing = newCurrentDrawing
        self.update_control_panel()

    def do_previous_fractal(self):
        if not self.previousStack.is_empty():
            self.do_next_previous(self.previousStack, self.nextStack)

    def draw_image_with_zoom(self):
        image = QtGui.QImage(WIDTH, HEIGHT, QtGui.QImage.Format_RGB888)
        painter = QtGui.QPainter()
        painter.begin(image)
        painter.drawImage(QtCore.QPoint(0, 0), self.currentDrawing.image)
        zoom = self.currentDrawing.zoomRect
        if zoom:
            pen = QtGui.QPen(QtCore.Qt.white)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(zoom.xUL, zoom.yUL, zoom.width, zoom.height)
            pen.setColor(QtCore.Qt.black)
            painter.setPen(pen)
            painter.drawRect(zoom.xUL+1, zoom.yUL+1, zoom.width-2, zoom.height-2)   
        painter.end()
        self.canvas.set_image(image)

    def make_complex_rectangle(self,drawing):
        # The maths for zooming...
        # We need a subset of drawing.fractalRect according to the drawing.zoomRect in pixels
        # And that needs to be scaled to match the image size
        iMin = drawing.fractalRect.iMin
        iMax = drawing.fractalRect.iMax
        rMin = drawing.fractalRect.rMin
        rMax = drawing.fractalRect.rMax

        if drawing.zoomRect == None:
            return ComplexRectangle(rMax,rMin,iMax,iMin)

        # delta is complex distance per pixel, should be same for V and H dimensions
        delta = (rMax - rMin) / WIDTH
        newRMin = rMin+(drawing.zoomRect.xUL * delta)
        newIMin = iMin+(HEIGHT - drawing.zoomRect.yUL- drawing.zoomRect.height)* delta
        newRMax = rMin+((drawing.zoomRect.xUL + drawing.zoomRect.width)* delta)
        newIMax = iMin+(HEIGHT - drawing.zoomRect.yUL)* delta
        complexWidth = newRMax - newRMin
        complexHeight = newIMax - newIMin
        imageWHRatio = WIDTH / HEIGHT
        complexWHRatio = complexWidth / complexHeight
        
        if imageWHRatio < complexWHRatio :
            #Expand vertically
            newHeight = complexWidth / imageWHRatio
            heightDifference = newHeight - complexHeight 
            newIMin = newIMin - heightDifference / 2
            newIMax = newIMax + heightDifference / 2
        else:
            # Expand horizontally
            newWidth = complexHeight * imageWHRatio
            widthDifference = newWidth - complexWidth
            newRMin = newRMin - widthDifference / 2
            newRMax = newRMax + widthDifference / 2
        return ComplexRectangle(newRMax,newRMin,newIMax,newIMin)

    def make_pixel_rectangle(self, x1, x2, y1, y2):
        x_ul = 0
        y_ul = 0
        width = 0
        height = 0
        if x1 > x2:
            x_ul = x2
            width = x1 - x2
        else:
            x_ul = x1
            width = x2 - x1
        if y1 > y2:
            y_ul = y2
            height = y1 - y2
        else:
            y_ul = y1
            height = y2 - y1
        return PixelRectangle( x_ul, y_ul, width, height )

    def update_control_panel(self):
        self.cm_list.setCurrentText(self.currentDrawing.cmName)
        if isinstance(self.currentDrawing, JuliaDrawing):
            self.mj_list.setCurrentText(JULIA)
        else:
            self.mj_list.setCurrentText(MANDLEBROT)
        if self.previousStack.is_empty():
            self.previous_button.setEnabled(False)
        else:
            self.previous_button.setEnabled(True)
        if self.nextStack.is_empty():
            self.next_button.setEnabled(False)
        else:
            self.next_button.setEnabled(True)
        if (not self.nextStack.is_empty()) or (not self.previousStack.is_empty()):
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)
        self.iterations_txt.setText(str(self.currentDrawing.maxIterations))
        self.previousIterations = self.currentDrawing.maxIterations
        self.draw_image_with_zoom() 

    ### ACTION LISTENERS

    def mouse_down_event(self,x,y):
        self.mousePosition= PixelPoint(x,y)
        self.mouseDown = True
        self.zoomClick = self.mousePosition

    def mouse_moved_event(self,x,y):
        self.mousePosition = PixelPoint(x,y)
        if self.juliaSelectMode:
            self.juliaPoint = self.calculate_julia_point(self.mousePosition)
            self.display_julia_point(self.juliaPoint)
        else:
            if self.mouseDown:
                zoom = self.make_pixel_rectangle(self.zoomClick.x,x,self.zoomClick.y,y)
                self.currentDrawing.set_zoom(zoom)
                self.draw_image_with_zoom()

    def mouse_up_event(self):
        self.mouseDown = False
        if self.juliaSelectMode:
            self.juliaPoint = self.calculate_julia_point(self.mousePosition)
            self.display_julia_point(self.juliaPoint)
            self.juliaSelectMode = False

    def on_color_map_change(self,cm):
        self.colorManager.setCM(cm)

    def on_delete_button_click(self):
        self.do_delete_fractal()

    def on_fractal_button_click(self):
        # Gather new drawing parameters
        image = QtGui.QImage(WIDTH, HEIGHT, QtGui.QImage.Format_RGB888)
        complexRect = INITIAL_MANDLEBROT_RECTANGLE
        mj = self.mj_list.currentText()
        if mj == JULIA:
            if isinstance(self.currentDrawing, JuliaDrawing) == False:
                complexRect = INITIAL_JULIA_RECTANGLE
            else:
                complexRect = self.make_complex_rectangle(self.currentDrawing)
            # Double the iterations for julia sets 
            maxIterations = 2 *int(self.determine_max_iterations(complexRect))
            newDrawing = JuliaDrawing(image, complexRect, WIDTH, HEIGHT, maxIterations, self.colorManager.currentCM,self.juliaPoint)
        else:
            if isinstance(self.currentDrawing, JuliaDrawing) == False:
                complexRect = self.make_complex_rectangle(self.currentDrawing)
            maxIterations = int(self.determine_max_iterations(complexRect))
            newDrawing = Drawing(image, complexRect, WIDTH, HEIGHT, maxIterations, self.colorManager.currentCM)
        self.do_make_new_fractal(newDrawing)

    def on_mj_change(self,mj):
        if mj == JULIA:
            self.juliaSelectMode = True
        else:
            self.juliaSelectMode = False

    def on_next_button_click(self):
        self.do_next_fractal()

    def on_previous_button_click(self):
        self.do_previous_fractal()

### THE PROGRAM: ###
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = FractalApp()
    window.show()
    sys.exit(app.exec_())
