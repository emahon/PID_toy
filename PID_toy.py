# keep an eye on the console - if the user types "pause", need to pause
# then prompt user for P, I, D, setpoint, and friction
# (give previous values when prompt)
# also allow the user to set the current state of the output
# as well as give options for sinusoidal and/or random disturbance


# simulate a system
# need the current position, rate of change, and rate of change of that



# implement a PID loop

# we don't want to loop as fast as possible, so we'll want a delay in the loop

# graph state of system

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import time

from matplotlib.widgets import Button

class pid_toy:
    def __init__(self):
        #system variables
        self.current_value = 0 # current position
        self.previous_value = 0 # previous position
        self.current_speed = 0
        self.friction_coefficient = 0
        self.friction_force = 0
        self.acceleration = 0
        self.control_force = 0

        #pid loop variables
        self.setpoint = 10
        self.error = 0
        self.error_sum = 0
        self.p_constant = .01
        self.i_constant = 0
        self.d_constant = 0
        self.control_input = 0

        #plotting variables
        self.loop_count = 0
        self.all_values = [0]*x_range

        self.paused = False
        self.curtext = axvalues.text(0.01, 0.7, "Value: " + "{:.2f}".format(self.current_value))
        self.setpointtext = axvalues.text(0.01,0.35, "Setpoint: " + str(self.setpoint))
        self.totalforce = axvalues.text(0.01,0.05, "Force: " + "{:.2f}".format(self.acceleration))

        self.ptext = axvalues.text(0.22,0.7,"P: " + str(self.p_constant))
        self.errtext = axvalues.text(0.22,0.35,"Error: " + "{:.2f}".format(self.error))
        self.ptottext = axvalues.text(0.22,0.05,"Total P: " + "{:.2f}".format(self.p_constant*self.error))

        self.itext = axvalues.text(0.42,0.7, "I: " + str(self.i_constant))
        self.cumerrtext = axvalues.text(0.42,0.35, "Summed error: " + "{:.2f}".format(self.error_sum*.01))
        self.itottext = axvalues.text(0.42,0.05, "Total I: " + "{:.2f}".format(self.i_constant*self.error_sum))

        self.dtext = axvalues.text(0.75,0.7, "D: " + str(self.d_constant))
        self.speedtext = axvalues.text(0.75,0.35, "Speed: " + "{:.2f}".format(self.current_speed))
        self.dtottext = axvalues.text(0.75,0.05, "Total D: " + "{:.2f}".format(self.d_constant*self.current_speed))
    
    def pause(self, event):
        print("paused")
        self.paused = True
        ani.event_source.stop()
        # get user input
        valid_p = False
        while (not valid_p):
            try:
                p_string = input("Set value of p: ")
                self.p_constant = float(p_string)
                valid_p = True
            except:
                print("Invalid value for p")
        valid_i = False
        while (not valid_i):
            try:
                i_string = input("Set value of i: ")
                self.i_constant = float(i_string)
                valid_i = True
            except:
                print("Invalid value for i")
        valid_d = False
        while (not valid_d):
            try:
                d_string = input("Set value of d: ")
                self.d_constant = float(d_string)
                valid_d = True
            except:
                print("Invalid value for d")

        self.error = 0
        self.error_sum = 0
        self.paused = False
        
        self.setpointtext.set_text("Setpoint: " + str(self.setpoint))
        self.ptext.set_text("P: " + str(self.p_constant))
        self.itext.set_text("I: " + str(self.i_constant))
        self.dtext.set_text("D: " + str(self.d_constant))
        self.setpointtext.set_text("Setpoint: " + str(self.setpoint))
        ani.event_source.start()
        

    #https://towardsdatascience.com/animations-with-matplotlib-d96375c5442c
    #https://learn.sparkfun.com/tutorials/graph-sensor-data-with-python-and-matplotlib/speeding-up-the-plot-animation
    def animate(self, i, line):
        #run
        # https://github.com/emahon/PID_toy/issues/12

        # correction force from PID controller

        self.current_speed = self.current_value - self.previous_value

        self.previous_value = self.current_value

        self.control_force = self.p_constant*self.error+self.i_constant*self.error_sum+self.d_constant*self.current_speed



        self.error_sum += self.error
        self.error = self.current_value - self.setpoint

        self.friction_force = self.friction_coefficient*self.current_speed

        # todo add ability for disturbance function, replace 0 with it
        self.acceleration = 0-self.friction_force-self.control_force

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

        self.curtext.set_text("Value: " + "{:.2f}".format(self.current_value))
        self.totalforce.set_text("Force: " + "{:.2f}".format(self.acceleration))
        
        self.errtext.set_text("Error: " + "{:.2f}".format(self.error))
        self.ptottext.set_text("Total P: " + "{:.2f}".format(self.p_constant*self.error))
        
        self.cumerrtext.set_text("Summed error: " + "{:.2f}".format(self.error_sum*.01))
        self.itottext.set_text("Total I: " + "{:.2f}".format(self.i_constant*self.error_sum))

        self.speedtext.set_text("Speed: " + "{:.2f}".format(self.current_speed))
        self.dtottext.set_text("Total D: " + "{:.2f}".format(self.d_constant*self.current_speed))
            
        return line, self.curtext, self.totalforce, self.setpointtext, self.ptext, self.errtext, self.ptottext, self.itext, self.cumerrtext, self.itottext, self.dtext, self.speedtext, self.dtottext, 

x_range = 150
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.3)
axpause = plt.axes([0.81, 0.05, 0.1, 0.075])

#axis to put text for values on
axvalues = plt.axes([0.05, 0.05, 0.7, 0.125])
#hide axes
axvalues.set_xticks([])
axvalues.set_yticks([])

xs = list(range(0,x_range))
ys = [0]*x_range
line, = ax.plot(xs, ys, lw=2)

pid_toy_instance = pid_toy()

ax.set_ybound(0,100)
ax.set_xlim(x_range,0)
bpause = Button(axpause, "Pause")
bpause.on_clicked(pid_toy_instance.pause)

ani = animation.FuncAnimation(
    fig,
    pid_toy_instance.animate,
    fargs=(line,),
    interval=(1.0/120.0)*1000.0,
    blit=True)
plt.show()
