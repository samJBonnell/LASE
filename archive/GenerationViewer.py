import matplotlib.pyplot as plt
import matplotlib
import numpy as np

trial = 'run08'
plotBest = False

with open("data/" + trial + "/history.csv") as file:
    data = [line.rstrip() for line in file]

with open("data/" + trial + "/generations.csv") as file:
    rawGenerationData = [line.rstrip() for line in file]

with open("data/" + trial + "/results.csv") as file:
    best = [float(line.rstrip()) for line in file]

mass = []
stress = []
for line in data:
    temp = line.split(',')
    mass.append(float(temp[1]))
    stress.append(float(temp[0]))

generations = []
previousIndex = 0
for line in rawGenerationData:
    temp = line.split(',')
    offSet = float(temp[1]) - previousIndex
    set = np.full(shape=int(offSet), fill_value=int(temp[0]))
    for gen in set:
        generations.append(gen)
    previousIndex = float(temp[1])

mass = mass[0:len(generations)]
stress = stress[0:len(generations)]
best = best[0:len(generations)]

fig, (ax1, ax2) = plt.subplots(2,1)
fig.suptitle("Case Study 5 - Stiffened Panel Optimization")
ax1.set_xlabel("Generation")
ax1.set_ylabel("Mass (kg)")
ax1.scatter(generations, mass, s=10, facecolors='none', edgecolors='b', marker='.')
ax1.set_yticks([1000, 2000, 3000, 4000, 5000, 6000])
ax1.set_ylim([0,6500])

if plotBest is True:
    ax1.scatter(list(range(1,max(generations) + 1)), best, s=3, facecolors='none', edgecolors='r', marker='X')

ax2.set_xlabel("Generation")
ax2.set_ylabel("Stress (Pa)")
ax2.scatter(generations, stress, s=10, facecolors='none', edgecolors='r', marker='.')
ax2.axhline(y=175000000, color='0', linestyle='--', label='Maximum Allowable Stress')
ax2.set_ylim([0,200000000])

plt.legend()
plt.show()