import Viewer
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

name = 'run03'
run = Viewer.Viewer(name)

[evaluations, generations, mass, stress, weldLength, best, variables] = run.data()
title = name + " - 300000 Pa Uniform Load"

# Plotting mass and stress as a function of simulation #
fig, (ax1, ax2) = plt.subplots(2,1)
fig.suptitle(title)

ax1.set_title("Variables vs. Simulation #")
ax1.set_ylabel("Mass (kg)")
ax1.scatter(evaluations, mass, s=10, facecolors='none', edgecolors='b', marker='.')
ax1.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000])
ax1.set_ylim([0,8000])

ax2.set_xlabel("Simulation Number")
ax2.set_ylabel("Stress (Pa)")
ax2.scatter(evaluations, stress, s=10, facecolors='none', edgecolors='r', marker='.')
ax2.axhline(y=175000000, color='0', linestyle='--', label='Maximum Allowable Stress')
ax2.set_ylim([0,250000000])

plt.legend()
plt.show()

if len(generations) == 0:
    exit()

# Plotting mass and stress as a function of generation #
fig, (ax1, ax2) = plt.subplots(2,1)
fig.suptitle(title)
ax1.set_title("Variables vs. Generation #")
ax1.set_ylabel("Mass (kg)")
ax1.scatter(generations, mass, s=10, facecolors='none', edgecolors='b', marker='.')
ax1.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000])
ax1.set_ylim([0,8000])

ax2.set_xlabel("Generation")
ax2.set_ylabel("Stress (Pa)")
ax2.scatter(generations, stress, s=10, facecolors='none', edgecolors='r', marker='.')
ax2.axhline(y=175000000, color='0', linestyle='--', label='Maximum Allowable Stress')
ax2.set_ylim([0,250000000])

plt.legend()
plt.show()

# Plotting variables as a function of generation #
fig, (ax1, ax2) = plt.subplots(2,1)
fig.suptitle(title)

variables = np.array(variables)
variables = variables.astype(np.float32)

labels = ["Plate Thickness", "TS Height", "TS Thickness", "TF Thickness", "TF Width", "LS Height", "LS Thickness", "LF Thickness", "LF Width", "# of TS", "# of TF"]

ax1.set_ylabel("# of Stiffeners")
ax1.scatter(generations, variables[:,0], s=10, marker='.', color='r')
ax1.set_ylim([0,12])
ax1.set_yticks([0, 2, 4, 6, 8, 10, 12])

ax2.set_ylabel("# of Stiffeners")
ax2.set_xlabel("Stiffener # vs. Generation")
ax2.scatter(generations, variables[:,1], s=10, marker='.', color='b')
ax2.set_ylim([0,12])
ax2.set_yticks([0, 2, 4, 6, 8, 10, 12])

plt.show()

# Show variables individually
labels = ["Plate Thickness", "TS Height", "TS Thickness", "TF Thickness", "TF Width", "LS Height", "LS Thickness", "LF Thickness", "LF Width", "# of TS", "# of TF"]
colours = ['#45e613', '#29ded1', '#360a9d', '#3d6064', '#15e8b2', '#f21ea1', '#f05340', '#89ab3b', '#b46d0b']
y_bounds = [[0,0.055], [0,1.1], [0,0.055],[0,0.055], [0,1.1], [0,1.1],[0,0.055],[0,0.055], [0,0.55]]

fig, ax = plt.subplots(3, 3, sharex=True)
fig.suptitle(title)

index = 0
for i in range(3):
    for j in range(3):
        col_name = i*3+j
        ax[i,j].scatter(generations, variables[:,col_name + 2], s=10, marker='.', label=labels[index],c=colours[index])
        ax[i,j].legend(fontsize=6)
        ax[i,j].set_ylim(y_bounds[index])
        index += 1

plt.show()

stress = np.array(stress)
mass = np.array(mass)
weldLength = np.array(weldLength)

variables = variables[stress[:] <= 175000000]
mass = mass[stress[:] <= 175000000]
weldLength = weldLength[stress[:] <= 175000000]

fig, ax1 = plt.subplots()
fig.suptitle("Pareto Front - Mass & Weld Length")

ax1.scatter(mass, weldLength, s=10, marker='.', color='r')

points = np.column_stack((mass, weldLength))
hull = ConvexHull(points)

for simplex in hull.simplices:
    ax1.plot(points[simplex, 0], points[simplex, 1], 'c')
ax1.plot(points[hull.vertices, 0], points[hull.vertices, 1], 'o', mec='r', color='none', lw=1, markersize=10)

ax1.set_xlabel("Mass (kg)")
ax1.set_ylabel("Weld Length (m)")

# ax1.set_yticks([range(0, max(weldLength), 10)])

plt.show()