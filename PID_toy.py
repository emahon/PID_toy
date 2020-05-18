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

import matplotlib.pyplot as plt
import time

from matplotlib.widgets import Button

#system variables
current_value = 0
previous_value = 0
speed = 0
friction = 0

#pid loop variables
setpoint = 10
error = 0
error_sum = 0
p_constant = .01
i_constant = 0
d_constant = 0
control_input = 0

#plotting variables
loop_count = 0
all_values = []

paused = False

fix, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
axpause = plt.axes([0.81, 0.05, 0.1, 0.075])

def pause(event):
    print("paused")
    global paused
    paused = True

while(True):
    if (paused):
        #wait for user input
        p_string = input("Set value of p: ")
        p_constant = float(p_string)*.01
        i_string = input("Set value of i: ")
        i_constant = float(i_string)*.00001
        d_string = input("Set value of d: ")
        d_constant = float(d_string)*.01
        paused = False
    else:
        #run
        error = setpoint - current_value
        error_sum += error
        speed = current_value - previous_value
        previous_value = current_value

        control_input = -1*(p_constant*error + i_constant*error_sum + d_constant*speed)

        current_value += (1-friction)*speed - control_input

        all_values.append(current_value)
        
        loop_count += 1
        
        ax.plot(range(loop_count), all_values, 'k')
        ax.set_ybound(0,100)
        ax.set_xlim(max(0, loop_count - 50), loop_count)
        bpause = Button(axpause, "Pause")
        bpause.on_clicked(pause)
        plt.pause(1.0/60.0)
