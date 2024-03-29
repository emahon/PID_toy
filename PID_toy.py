# then prompt user for P, I, D, setpoint, and friction
# (give previous values when prompt)
# also allow the user to set the current state of the output
# as well as give options for sinusoidal and/or random disturbance


# simulate a system
# need the current position, rate of change, and rate of change of that



# implement a PID loop

# graph state of system

import math
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import PyQt5
import random
import sys
import time

from enum import Enum
from matplotlib.figure import Figure
from matplotlib.widgets import Button

# https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_qt_sgskip.html
from matplotlib.backends.qt_compat import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PyQt5.QtCore import pyqtRemoveInputHook, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QSlider, QDoubleSpinBox, QLabel, QAbstractSpinBox

class PID_Toy(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        #
        # initialize calculation stuff
        #

        #format constant
        self.format = "{: .1e}"

        #system variables
        self.current_value = 0 # current position
        self.previous_value = 0 # previous position
        self.current_speed = 0
        self.friction_coefficient = 0
        self.friction_force = 0
        self.acceleration = 0
        self.control_force = 0

        #pid loop variables
        self.setpoint = 50
        self.error = 0
        self.error_sum = 0
        self.error_speed = 0
        self.p_constant = .001
        self.i_constant = .000005
        self.d_constant = .04
        self.control_input = 0
        self.maximum_control_input = .01

        # disturbance variables
        self.maximum_disturbance = .02
        self.disturbance_func = Disturbance.NONE
        self.disturbance_freq = 0
        self.disturbance_val = 0
        self.ext_setpoint = self.setpoint
        self.ext_setpoint_k = 0

        #plotting variables
        self.loop_count = 0
        self.all_values = [0]*x_range
        self.timestep = 1.0/120.0 # should be in seconds

        self.paused = False
        self.curtext = axvalues.text(0.01, 0.7, "Value: " + self.format.format(self.current_value))
        self.setpointtext = axvalues.text(0.01,0.35, "Setpoint: " + self.format.format(self.setpoint))
        self.totalforce = axvalues.text(0.01,0.05, "Force: " + self.format.format(self.acceleration))

        self.ptext = axvalues.text(0.22,0.7,"P: " + self.format.format(self.p_constant))
        self.errtext = axvalues.text(0.22,0.35,"Error: " + self.format.format(self.error))
        self.ptottext = axvalues.text(0.22,0.05,"Total P: " + self.format.format(self.p_constant*self.error))

        self.itext = axvalues.text(0.42,0.7, "I: " + self.format.format(self.i_constant))
        self.cumerrtext = axvalues.text(0.42,0.35, "Summed error: " + self.format.format(self.error_sum))
        self.itottext = axvalues.text(0.42,0.05, "Total I: " + self.format.format(self.i_constant*self.error_sum))

        self.dtext = axvalues.text(0.75,0.7, "D: " + self.format.format(self.d_constant))
        self.speedtext = axvalues.text(0.75,0.35, "Speed: " + self.format.format(self.current_speed))
        self.dtottext = axvalues.text(0.75,0.05, "Total D: " + self.format.format(self.d_constant*self.current_speed))

        #
        # initialize visualization stuff
        #

        self._main = QtWidgets.QWidget()
        #self._main.setLayout(layout)
        self.setCentralWidget(self._main)
        layout = QtWidgets.QGridLayout(self._main, spacing=10)

        xs = list(range(0,x_range))
        ys = [0]*x_range
        line, = ax.plot(xs, ys, lw=2)
        setpointline, = ax.plot(xs, ys, lw=2)

        ax.set_ybound(0,100)
        ax.set_xlim(x_range,0)

        print("before animation")

        canvas = FigureCanvas(fig)
        
        self.ani = animation.FuncAnimation(
            fig,
            self.animate,
            fargs=(line,setpointline),
            interval=(self.timestep)*1000.0,
            blit=True)  

        layout.addWidget(canvas, 0, 0, 1, 5) # row, column, rowSpan, columnSpan
        self.addToolBar(NavigationToolbar(canvas, self))

        # pause button
        self.button = QPushButton("Pause")
        layout.addWidget(self.button, 3, 4)
        self.button.setCheckable(True)
        self.button.clicked.connect(self.pause)
        self.button.show()

        # Current value editor
        self.cur_val_precision = 2
        cur_val_min = 0
        cur_val_max = 100

        cur_val_label = QLabel()
        cur_val_label.setText("Set Value")
        layout.addWidget(cur_val_label, 2, 0)

        # Current value slider
        self.cur_val_slider = QSlider(Qt.Horizontal)
        layout.addWidget(self.cur_val_slider, 3, 0)
        self.cur_val_slider.setMinimum(cur_val_min)
        self.cur_val_slider.setMaximum(cur_val_max*(10**self.cur_val_precision))
        # to-do: how to show the appropriate tick values?
        #self.cur_val_slider.setTickPosition(QSlider.TicksBelow)
        #self.cur_val_slider.setTickInterval(10)
        self.cur_val_slider.valueChanged.connect(self.handleCurValSliderChange)
        self.cur_val_slider.show()

        # Current value input box
        self.cur_val_input = QDoubleSpinBox()
        layout.addWidget(self.cur_val_input, 3, 1)
        self.cur_val_input.setMinimum(cur_val_min)
        self.cur_val_input.setMaximum(cur_val_max)
        self.cur_val_input.valueChanged.connect(self.handleCurValInputChange)
        self.cur_val_input.show()

        # Setpoint editor
        setpoint_label = QLabel()
        setpoint_label.setText("Setpoint")
        layout.addWidget(setpoint_label, 4, 0)

        # Setpoint slider
        self.setpoint_slider = QSlider(Qt.Horizontal)
        layout.addWidget(self.setpoint_slider, 5, 0)
        self.setpoint_slider.setMinimum(cur_val_min)
        self.setpoint_slider.setMaximum(cur_val_max*(10**self.cur_val_precision))
        #self.setpoint_slider.setTickPosition(QSlider.TicksBelow)
        #self.setpoint_slider.setTickInterval(10)
        self.setpoint_slider.valueChanged.connect(self.handleSetpointSliderChange)
        self.setpoint_slider.show()

        # Setpoint input box
        self.setpoint_input = QDoubleSpinBox()
        layout.addWidget(self.setpoint_input, 5, 1)
        self.setpoint_input.setMinimum(cur_val_min)
        self.setpoint_input.setMaximum(cur_val_max)
        self.setpoint_input.valueChanged.connect(self.handleSetpointInputChange)
        self.setpoint_input.show()

        # P value editing
        p_min = -100
        p_max = 100

        p_label = QLabel()
        p_label.setText("P")
        layout.addWidget(p_label, 2, 2)

        # P value slider
        self.p_slider = QSlider(Qt.Horizontal)
        layout.addWidget(self.p_slider, 3, 2)
        self.p_slider.show()

        # P value input box
        self.p_input = QDoubleSpinBox()
        self.p_input.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        layout.addWidget(self.p_input, 3, 3)
        self.p_input.show()
        

    def handleCurValSliderChange(self, value):
        realVal = value/(10.0**self.cur_val_precision)
        self.cur_val_input.setValue(realVal)
        self.current_value = realVal
        self.curtext.set_text("Value: " + self.format.format(self.current_value))

    def handleCurValInputChange(self, value):
        self.cur_val_slider.setValue(math.floor(value*(10**self.cur_val_precision)))
        self.current_value = value
        self.curtext.set_text("Value: " + self.format.format(self.current_value))

    def handleSetpointSliderChange(self, value):
        realVal = value/(10.0**self.cur_val_precision)
        self.setpoint_input.setValue(realVal)
        self.setpoint = realVal
        self.setpointtext.set_text("Setpoint: " + self.format.format(self.setpoint))

    def handleSetpointInputChange(self, value):
        self.setpoint_slider.setValue(math.floor(value*(10**self.cur_val_precision)))
        self.setpoint = value
        self.setpointtext.set_text("Setpoint: " + self.format.format(self.setpoint))



    def pause(self, event):
        self.button.setEnabled(False)
        if (self.paused):
            return
        print("paused")
        self.paused = True
        self.ani.event_source.stop()
        print("Hit enter to skip input and keep variable at current value")
        # get user input
        valid_p = False
        while (not valid_p):
            try:
                p_string = input("Set value of p: ")
                if (p_string == ""):
                    valid_p = True
                    break
                self.p_constant = float(p_string)
                valid_p = True
            except:
                print("Invalid value for p")
        valid_i = False
        while (not valid_i):
            try:
                i_string = input("Set value of i: ")
                if (i_string == ""):
                    valid_i = True
                    break
                self.i_constant = float(i_string)
                valid_i = True
            except:
                print("Invalid value for i")
        valid_d = False
        while (not valid_d):
            try:
                d_string = input("Set value of d: ")
                if (d_string == ""):
                    valid_d = True
                    break
                self.d_constant = float(d_string)
                valid_d = True
            except:
                print("Invalid value for d")

        valid_setpoint = False
        while (not valid_setpoint):
            try:
                set_string = input("Setpoint value: ")
                if (set_string == ""):
                    valid_setpoint = True
                    break
                parsed_setpoint = float(set_string)
                valid_setpoint = (parsed_setpoint >= 0) and (parsed_setpoint <= 100)
                if (valid_setpoint):
                    self.setpoint = parsed_setpoint
            except:
                print("Invalid setpoint")

        valid_vc = False
        while (not valid_vc):
            try:
                vc_string = input("Current value: ")
                if (vc_string == ""):
                    valid_vc = True
                    break
                parsed_vc = float(vc_string)
                valid_vc = (parsed_vc >= 0) and (parsed_vc <= 100)
                if (valid_vc):
                    self.current_value = parsed_vc
            except:
                print("Invalid value")

        self.error = 0
        self.error_sum = 0
        self.paused = False
        
        self.ptext.set_text("P: " + self.format.format(self.p_constant))
        self.itext.set_text("I: " + self.format.format(self.i_constant))
        self.dtext.set_text("D: " + self.format.format(self.d_constant))
        self.setpointtext.set_text("Setpoint: " + self.format.format(self.setpoint))
        self.curtext.set_text("Value: " + self.format.format(self.current_value))
        self.ani.event_source.start()
        self.button.setChecked(False)
        self.button.setEnabled(True)

    #https://towardsdatascience.com/animations-with-matplotlib-d96375c5442c
    #https://learn.sparkfun.com/tutorials/graph-sensor-data-with-python-and-matplotlib/speeding-up-the-plot-animation
    def animate(self, i, line, setpointline):
        #run
        # https://github.com/emahon/PID_toy/issues/12

        # correction force from PID controller
        print("blah")

        self.current_speed = self.current_value - self.previous_value

        self.previous_value = self.current_value

        self.control_force = self.p_constant*self.error+self.i_constant*self.error_sum+self.d_constant*self.error_speed

        if (self.control_force > self.maximum_control_input):
            self.control_force = self.maximum_control_input
        elif (self.control_force < -1*self.maximum_control_input):
            self.control_force = -1*self.maximum_control_input

        self.error_sum += self.error
        prev_error = self.error
        self.error = self.current_value - self.setpoint
        self.error_speed = self.error - prev_error

        self.friction_force = self.friction_coefficient*self.current_speed*self.current_speed

        # todo add ability for disturbance function, replace 0 with it
        dist = 0
        
        if (self.disturbance_func == Disturbance.RANDOM):
            dist = self.maximum_disturbance*(2*random.random() - 1)
        elif (self.disturbance_func == Disturbance.SINE):
            dist = self.maximum_disturbance*math.sin(2*math.pi) # todo: frequency stuff
        elif (self.disturbance_func == Disturbance.CONST):
            dist = self.maximum_disturbance*self.disturbance_val
        elif (self.disturbance_func == Disturbance.SQUARE):
            dist = 0
        elif (self.disturbance_func == Disturbance.HELL):
            dist = 0
        elif (self.disturbance_func == Disturbance.EXTSET):
            dist = 0
        elif (self.disturbance_func == Disturbance.PERIOD):
            dist = 0

        self.acceleration = dist-self.friction_force-self.control_force

        self.speedtext.set_text("Speed: " + self.format.format(self.current_speed))

        self.current_speed = self.current_speed + self.acceleration

        self.current_value = self.current_value + self.current_speed

        if (self.current_value > 100):
            self.current_value = 100
        elif (self.current_value < 0):
            self.current_value = 0

        self.all_values.append(self.current_value)
        self.all_values = self.all_values[-x_range:]
        
        self.loop_count += 1
        
        list_to_reverse = list(self.all_values)
        list_to_reverse.reverse()
        line.set_ydata(list_to_reverse)
        setpointline.set_ydata([self.setpoint]*x_range)

        self.curtext.set_text("Value: " + self.format.format(self.current_value))
        self.totalforce.set_text("Force: " + self.format.format(self.acceleration))
        
        self.errtext.set_text("Error: " + self.format.format(self.error))
        self.ptottext.set_text("Total P: " + self.format.format(self.p_constant*self.error))
        
        self.cumerrtext.set_text("Summed error: " + self.format.format(self.error_sum))
        self.itottext.set_text("Total I: " + self.format.format(self.i_constant*self.error_sum))

        self.dtottext.set_text("Total D: " + self.format.format(self.d_constant*self.error_speed))
            
        return line, setpointline, self.curtext, self.totalforce, self.setpointtext, self.ptext, self.errtext, self.ptottext, self.itext, self.cumerrtext, self.itottext, self.dtext, self.speedtext, self.dtottext,



class Disturbance(Enum):
    NONE = 0
    RANDOM = 1
    SINE = 2
    CONST = 3
    SQUARE = 4
    HELL = 5
    EXTSET = 6
    PERIOD = 7        

    
if (__name__ == '__main__'):
    # https://stackoverflow.com/questions/40177743/why-does-input-cause-qcoreapplicationexec-the-event-loop-is-already-runnin
    pyqtRemoveInputHook()

    x_range = 150

    fig, ax = plt.subplots(figsize=(10,7)) # units are inches
    plt.subplots_adjust(bottom=0.3)

    #axis to put text for values on
    axvalues = plt.axes([0.05, 0.05, 0.7, 0.125])
    #hide axes
    axvalues.set_xticks([])
    axvalues.set_yticks([])

    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = PID_Toy()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec_()
