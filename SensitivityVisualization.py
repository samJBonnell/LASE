import Viewer
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull

name = 'run01'
run = Viewer.Viewer(name)

MeshSize = []
Stress = []
MeshSize2 = []
Stress2 = []
MeshSize3 = []
Stress3 = []
MeshSize4 = []
Stress4 = []

with open("sensitivity/" + name + "/results.csv") as file:
    temp = [line.rstrip() for line in file]
    for line in temp:
        temp = line.split(',')
        MeshSize.append(float(temp[0]))
        Stress.append(float(temp[1])/1e6)

name = 'run02'
with open("sensitivity/" + name + "/results.csv") as file:
    temp = [line.rstrip() for line in file]
    for line in temp:
        temp = line.split(',')
        MeshSize2.append(float(temp[0]))
        Stress2.append(float(temp[1])/1e6)

name = 'run03'
with open("sensitivity/" + name + "/results.csv") as file:
    temp = [line.rstrip() for line in file]
    for line in temp:
        temp = line.split(',')
        MeshSize3.append(float(temp[0]))
        Stress3.append(float(temp[1])/1e6)

name = 'run04'
with open("sensitivity/" + name + "/results.csv") as file:
    temp = [line.rstrip() for line in file]
    for line in temp:
        temp = line.split(',')
        MeshSize4.append(float(temp[0]))
        Stress4.append(float(temp[1])/1e6)

# title = name + " - Plate Mesh Dependance"
title = "All Trials Superimposed - Plate Mesh Dependance"

# Plotting mass and stress as a function of simulation #
fig, ax1 = plt.subplots()
fig.suptitle(title)

ax1.set_title("Stress (MPa) vs. Plate Mesh Size (m)")
ax1.set_ylabel("Von Mises Stress (MPa)")
ax1.set_xlabel("Plate Mesh Size (m)")

ax1.scatter(MeshSize, Stress, s=20, facecolors='none', edgecolors='b', marker='.', label="run01")
ax1.scatter(MeshSize2, Stress2, s=20, facecolors='none', edgecolors='r', marker='.',label="run02")
ax1.scatter(MeshSize3, Stress3, s=20, facecolors='none', edgecolors='g', marker='.',label="run03")
ax1.scatter(MeshSize4, Stress4, s=20, facecolors='none', edgecolors='y', marker='.',label="run04")


# ax1.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
# ax1.set_xlim([0,max(MeshSize) + min(MeshSize)])
# ax1.set_ylim([0,max(Stress)+100])

plt.legend()
plt.show()