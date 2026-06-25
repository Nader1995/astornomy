import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the Excel file
file_path = 'final_processed_data.csv'
final_processed_data = pd.read_csv(file_path)

file_path2 = "output53502492214.csv"  # Change this to the correct file path
file4 = pd.read_csv(file_path2)

# Define the distance constant (now set to 172.4)
d_c = 172.4

# Calculate x_axis3 and y_axis3 (for the blue isochrone line)
x_axis3 = file4['Jmag'] - file4['Ksmag']
y_axis3 = file4['Jmag'] + (5 * np.log10(d_c) - 5)

x_axis2 = final_processed_data['Jmag[mag]'] - final_processed_data['Kmag[mag]']
y_axis2 = final_processed_data['Jmag[mag]']

# Convert e_Jmag[mag] and e_Kmag[mag] to numeric, set errors='coerce' to turn non-numeric values into NaN
final_processed_data['e_Jmag[mag]'] = pd.to_numeric(final_processed_data['e_Jmag[mag]'], errors='coerce')
final_processed_data['e_Kmag[mag]'] = pd.to_numeric(final_processed_data['e_Kmag[mag]'], errors='coerce')

# Add sigma error column (average error in pmRA and pmDE, multiplied by 2.5)
final_processed_data['sigma'] = (
    ((final_processed_data['e_Jmag[mag]'] + final_processed_data['e_Kmag[mag]']) / 2) * 2.5
)

# Optionally, handle NaN values in 'sigma' (e.g., replace with a default value or drop rows with NaN)
final_processed_data['sigma'].fillna(0, inplace=True)  # This fills NaN with 0, or use another strategy

# List to store the new blue points (including original ones)
x_all_points = []
y_all_points = []

# Loop through each pair of consecutive blue points
for i in range(len(x_axis3) - 1):
    # Get the current and next blue point
    x_start, y_start = x_axis3.iloc[i], y_axis3.iloc[i]
    x_end, y_end = x_axis3.iloc[i + 1], y_axis3.iloc[i + 1]

    # Add the starting point to the list
    x_all_points.append(x_start)
    y_all_points.append(y_start)

    # Generate 100 points between the current and next blue point (linear interpolation)
    for j in range(1, 1001):
        t = j / 1001  # parameter to interpolate
        x_new = x_start + t * (x_end - x_start)
        y_new = y_start + t * (y_end - y_start)

        # Add the interpolated point to the list
        x_all_points.append(x_new)
        y_all_points.append(y_new)

# Add the final blue point to the list (last one)
x_all_points.append(x_axis3.iloc[-1])
y_all_points.append(y_axis3.iloc[-1])

# Now filter the points based on the conditions:
# 1. Remove points where y < 0
# 2. Keep x-values between -0.2 and 1.2

filtered_x_points = []
filtered_y_points = []

for x, y in zip(x_all_points, y_all_points):
    if 5 <= y <= 20 and -0.2 <= x <= 1.2:
        filtered_x_points.append(x)
        filtered_y_points.append(y)

# Now compare the red dots (from x_axis2, y_axis2) with the filtered blue points

# Create a mask to mark which red points should be removed
remove_red_mask = np.ones(len(x_axis2), dtype=bool)

for i in range(len(x_axis2)):
    red_x = x_axis2.iloc[i]
    red_y = y_axis2.iloc[i]
    sigma = final_processed_data['sigma'].iloc[i]

    # Check if there is a blue point close to this red point
    for blue_x, blue_y in zip(filtered_x_points, filtered_y_points):
        if np.abs(red_y - blue_y) < 0.001:  # Adjust the proximity threshold as needed
            # Check if the x-coordinate difference is less than the sigma for that red point
            if np.abs(red_x - blue_x) > sigma:
                # Mark this red point to be removed
                remove_red_mask[i] = False
                break  # No need to check further if the point is marked for removal

# Filter the remaining red points based on the mask
remaining_red_x = x_axis2[remove_red_mask]
remaining_red_y = y_axis2[remove_red_mask]

# Plot the filtered blue points and the remaining red points
plt.figure(5)
plt.gca().invert_yaxis()  # To invert the y-axis
plt.ylim([20, -10])
plt.xlim([-0.25, 1.25])

# Scatter plot for the filtered blue points
plt.scatter(filtered_x_points, filtered_y_points, marker=".", color="blue", label="Filtered Isochrone points", s=6)

# Scatter plot for the remaining red points
plt.scatter(remaining_red_x, remaining_red_y, marker=".", color="red", label="Remaining Astrometrically selected stars", s=2)

# Add labels and title
plt.xlabel("J-K [mag]")
plt.ylabel("J [mag]")
plt.title("Filtered Color-Magnitude Diagram\n with Interpolated Isochrone Points")
plt.legend(loc="upper left")
plt.show()

print(len(remaining_red_x))
