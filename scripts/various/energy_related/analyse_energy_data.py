import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
path = 'lodia_planner/src/energyanalysis/'
df = pd.read_csv(path+'20230908171356/joint_acceleration_drive.csv')  # Replace with the actual file path

# Assuming the column you want to plot is 'Value 1' (change it to the actual column name)
column_to_plot = 'Value 1'

# Plot the data
plt.plot(df[column_to_plot])
plt.xlabel('Index')
plt.ylabel(column_to_plot)
plt.title(f'Plot of {column_to_plot}')
plt.show()
