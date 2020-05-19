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
        self.current_value = 0
        self.previous_value = 0
        self.speed = 0
        self.friction = 0

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
        self.all_values = []

        self.paused = False
    
    def pause(self, event):
        print("paused")
        self.paused = True

    #https://towardsdatascience.com/animations-with-matplotlib-d96375c5442c
    def animate(self, i):
        if (self.paused):
            #wait for user input
            p_string = input("Set value of p: ")
            self.p_constant = float(p_string)*.01
            i_string = input("Set value of i: ")
            self.i_constant = float(i_string)*.00001
            d_string = input("Set value of d: ")
            self.d_constant = float(d_string)*.01        
            self.paused = False
        else:
            #run
            self.error = self.setpoint - self.current_value
            self.error_sum += self.error
            self.speed = self.current_value - self.previous_value
            self.previous_value = self.current_value

            self.control_input = (self.p_constant*self.error + self.i_constant*self.error_sum - self.d_constant*self.speed)

            self.current_value += (1-self.friction)*self.speed + self.control_input

            self.all_values.append(self.current_value)
            
            self.loop_count += 1
            
            ax.clear()
            ax.plot(range(self.loop_count), self.all_values, 'k')
            ax.set_ybound(0,100)
            ax.set_xlim(max(0, self.loop_count - 50), self.loop_count)
            bpause = Button(axpause, "Pause")
            bpause.on_clicked(self.pause)

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
axpause = plt.axes([0.81, 0.05, 0.1, 0.075])

pid_toy_instance = pid_toy()

ani = animation.FuncAnimation(fig, pid_toy_instance.animate, interval=(1.0/60.0)*1000.0)
plt.show()
