import matplotlib.pyplot as plt
import matplotlib
import numpy as np

trial = 'run06'

with open("data/" + trial + "/history.csv") as file:
    lines = [line.rstrip() for line in file]

mass = []
stress = []
for line in lines:
    temp = line.split(',')
    mass.append(float(temp[1]))
    stress.append(float(temp[0]))

evals = range(1,len(lines) + 1)

fig, (ax1, ax2) = plt.subplots(2,1)
fig.suptitle("Case Study 4 - Stiffened Panel Optimization")
ax1.set_xlabel("Simulation Number")
ax1.set_ylabel("Mass (kg)")
ax1.scatter(evals, mass, s=10, facecolors='none', edgecolors='b', marker='.')
ax1.set_yticks([1000, 2000, 3000, 4000, 5000, 6000])
ax1.set_ylim([0,6500])

ax2.set_xlabel("Simulation Number")
ax2.set_ylabel("Stress (Pa)")
ax2.scatter(evals, stress, s=10, facecolors='none', edgecolors='r', marker='.')
ax2.axhline(y=175000000, color='0', linestyle='--', label='Maximum Allowable Stress')

plt.legend()
plt.show()