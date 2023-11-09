import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
import threading
import time
import os


# Function to clear the console
def clear_console():
  os.system('cls' if os.name == 'nt' else 'clear')


# Function to export the results to a text file
def export_results_to_txt(slope, intercept, red_below_line, blue_below_line):
  with open("simulation_results.txt", "a") as file:  # Use "a" for append mode
    file.write(f"Slope: {slope}\n")
    file.write(f"Intercept: {intercept}\n")
    file.write(f"Red Dots Below Line (Unsafe): {red_below_line}\n")
    file.write(f"Blue Dots Below Line (Safe): {blue_below_line}\n")
    file.write("\n")  # Add a newline to separate entries


# Function to count how many dots are correctly classified
def count_correct_classifications(slope, intercept, red_dots, blue_dots):
  red_correct = np.sum(red_dots[:, 1] >= (slope * red_dots[:, 0] + intercept))
  blue_correct = np.sum(
      blue_dots[:, 1] < (slope * blue_dots[:, 0] + intercept))
  return red_correct + blue_correct


# Optimization step function
def optimization_step(slope, intercept, red_dots, blue_dots, step_size=0.1):
  current_score = count_correct_classifications(slope, intercept, red_dots,blue_dots)

  # Try adjusting the slope
  slope_increase = count_correct_classifications(slope + step_size, intercept,red_dots, blue_dots)
  slope_decrease = count_correct_classifications(slope - step_size, intercept,red_dots, blue_dots)

  if slope_increase > current_score:
    slope += step_size
  elif slope_decrease > current_score:
    slope -= step_size

  # Try adjusting the intercept
  intercept_increase = count_correct_classifications(slope,intercept + step_size,red_dots, blue_dots)
  intercept_decrease = count_correct_classifications(slope,intercept - step_size,
red_dots, blue_dots)

  if intercept_increase > current_score:
    intercept += step_size
  elif intercept_decrease > current_score:
    intercept -= step_size

  return slope, intercept


# Initialize parameters
num_red_dots = 50
num_blue_dots = 50
line_slope = 1
line_intercept = 0

# Create a figure and a subplot
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.35)

# Generate random points for red and blue dots
red_dots = np.random.rand(num_red_dots, 2) * 10
blue_dots = np.random.rand(num_blue_dots, 2) * 10

# Plot red and blue dots
ax.scatter(red_dots[:, 0], red_dots[:, 1], color='red', label='Unsafe')
ax.scatter(blue_dots[:, 0], blue_dots[:, 1], color='blue', label='Safe')

# Draw the initial decision line
line, = ax.plot([0, 10], [line_intercept, line_slope * 10 + line_intercept],
                'k-')

# Add sliders for slope and intercept
ax_slope = plt.axes([0.1, 0.2, 0.8, 0.03], facecolor='lightgoldenrodyellow')
ax_intercept = plt.axes([0.1, 0.15, 0.8, 0.03],
                        facecolor='lightgoldenrodyellow')
slope_slider = Slider(ax_slope, 'Slope', 0.1, 10.0, valinit=line_slope)
intercept_slider = Slider(ax_intercept,'Intercept',-5.0,5.0,valinit=line_intercept)

# Add a button for optimization
ax_button = plt.axes([0.8, 0.05, 0.1, 0.04])
button = Button(ax_button,'Optimize',color='lightgoldenrodyellow',
hovercolor='0.975')


# Function to fill the area covered by the line with yellow
def fill_area_below_line(slope, intercept):
  x = np.linspace(0, 10, 100)
  y = slope * x + intercept
  plt.fill_between(x, 0, y, where=(y >= 0), color='yellow', alpha=0.5)


# Update function to adjust the line and print the simulation results
def update(val):
  clear_console()
  slope = slope_slider.val
  intercept = intercept_slider.val
  line.set_ydata([intercept, slope * 10 + intercept])
  fill_area_below_line(slope, intercept)  # Fill the area below the line
  red_below_line = np.sum(
      red_dots[:, 1] < (slope * red_dots[:, 0] + intercept))
  blue_below_line = np.sum(
      blue_dots[:, 1] < (slope * blue_dots[:, 0] + intercept))
  print_simulation_results(slope, intercept)

  export_results_to_txt(slope, intercept, red_below_line,
                        blue_below_line)  # Export results to txt
  fig.canvas.draw_idle()


# Function to print the simulation results
def print_simulation_results(slope, intercept):
  red_below_line = np.sum(
      red_dots[:, 1] < (slope * red_dots[:, 0] + intercept))
  blue_below_line = np.sum(
      blue_dots[:, 1] < (slope * blue_dots[:, 0] + intercept))
  print(f"Red Dots Below Line (Unsafe): {red_below_line}")
  print(f"Blue Dots Below Line (Safe): {blue_below_line}")


# Function to run simulations
def run_simulations(num_simulations):
  simulation_count = 0  # Initialize the simulation count
  while simulation_count < num_simulations:
    global line_slope, line_intercept
    line_slope = np.random.uniform(0.1, 10.0)  # Random slope
    line_intercept = np.random.uniform(-5.0, 5.0)  # Random intercept
    slope_slider.set_val(line_slope)
    intercept_slider.set_val(line_intercept)
    update(0)  # Update the plot and print results
    simulation_count += 1


# Button click event handler
def optimize(event):
  global line_slope, line_intercept
  line_slope, line_intercept = optimization_step(line_slope, line_intercept,
                                                 red_dots, blue_dots)
  slope_slider.set_val(line_slope)
  intercept_slider.set_val(line_intercept)


# Connect the update function to the sliders and button
slope_slider.on_changed(update)
intercept_slider.on_changed(update)
button.on_clicked(optimize)


# Function to randomly move the line for a set number of simulations
def move_line_randomly(num_simulations):
    global line_slope, line_intercept
    for _ in range(num_simulations):
        time.sleep(1)  # Sleep for 1 second
        line_slope = np.random.uniform(0.1, 10.0)  # Random slope
        line_intercept = np.random.uniform(-5.0, 5.0)  # Random intercept
        slope_slider.set_val(line_slope)
        intercept_slider.set_val(line_intercept)
        update(0)  # Update the plot and print results

# Set the number of simulations you want to run
num_simulations = 5  # Replace 5 with your desired number of simulations

# Create and start the thread for moving the line randomly
line_thread = threading.Thread(target=move_line_randomly, args=(num_simulations,))
line_thread.daemon = True
line_thread.start()

# Initialize the update function
update(0)

# Set the title of the window
fig.canvas.manager.set_window_title('Forest')

# Show the plot with a legend
ax.legend()

# This call will block the main thread, so make sure all other threads are started before this
plt.show()