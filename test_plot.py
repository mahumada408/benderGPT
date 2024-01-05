import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Create the data
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# Create the plot
plt.plot(x, y)

# Set the title and labels
plt.title("Test Plot")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")

# Show the plot
plt.show()
