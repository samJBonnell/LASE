# - Case Study 3
# 	- Panel from Yeunchen paper
# 	- Minimize mass
# 	- Make sure no point exceeds 175MPa
# 	- Continuous panel thickness

# Use NSGA-II algorithm to start...

# We want to minimize mass with continous panel thickness, and ensure that NO point exceeds 175MPa of stress
# Define the set of variables that can exist and bounds:
# 1. Number of transverse stiffeners:    2 < x < 4
# 2. Number of longitudinal stiffeners:  2 < x < 7
# 3. Plate thickness:                    0.005 < x < 0.05
# 4. Transvers Stiffener Height:         0.050 < x < 1.00
# 5. Transverse Stiffener thickness:     0.005 < x < 0.05      
# 6. Transverse Flange thickness:        0.005 < x < 0.05
# 7. Transverse Flange width:            0.010 < x < 0.75
# 8. Longitudinal Stiffener Height:      0.010 < x < 0.95
# 9. Longitudinal Stiffener thickness:   0.005 < x < 0.05
# 10. Longitudinal Flange thickness:     0.005 < x < 0.05
# 11. Longitudinal Flange width:         0.010 < x < 0.50

# Further constraints exist due to the limiting description of the panel in ABAQUS:
# 1. Height of Transverse Stiffeners > Height of Longitudinal Stiffeners

# Python Imports
import numpy as np
import time
import subprocess
import matplotlib.pyplot as plt

# Pymoo Imports
from pymoo.core.problem import ElementwiseProblem

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling

start_time = time.time()

class StiffenedPanelOptimizationCS3(ElementwiseProblem):
    def __init__(self):
        super().__init__(n_var=11,
                         n_obj=1,
                         n_ieq_constr=2,
                         xl = np.array([2, 2, 0.005, 0.05, 0.005, 0.005, 0.010, 0.010, 0.005, 0.005, 0.010]),
                         xu = np.array([4, 7, 0.050, 1.00, 0.050, 0.050, 0.750, 0.950, 0.050, 0.050, 0.500]))

    def _evaluate(self, x, out, *args, **kwargs):

        # Create 'template' integer values for stiffener numbers
        x[0] = round(x[0], 0)
        x[1] = round(x[1], 0)
        
        # for index in range(2,len(x)):
        #     x[index] = round(x[index], 3)

        if x[7] >= x[3]:
            x[7] = x[3] - 0.0001

        # Generate variable list to send to ABAQUS
        outputData = ""
        for index in range(len(x)):
            outputData += str(x[index]) + ","

        
        outputData += '\n'

        # Write the variable sequence to the ABAQUS transfer file
        output = open("temp\\optimizationFile.csv", 'a')
        output.write(outputData)
        output.close()

        # Function call to the ABAQUS module & wait for function call to complete
        functionCall = subprocess.Popen(["abaqus", "cae", "noGUI=StiffenedPanelPythonScript.py"], shell=True)
        functionCall.communicate()

        # Once the program is done running, 
        with open("temp\\abaqusOutput.csv") as file:
            lines = [line.rstrip() for line in file]

        # The objective function is to minimze the mass of the panel
        f1 = float(lines[1])

        # Constraints are defined by max stress & geometric tolerancing due to assignment in ABAQUS
        g1 = float(lines[0]) - 1.75e+8
        g2 = x[7] - x[3]

        out["F"] = [f1]
        out["G"] = [g1, g2]

        print(algorithm.n_gen)

        writeHistory = open("temp\\history.csv", 'a')
        writeHistory.write(str(lines[0]) + "," + str(lines[1]) + "\n")
        writeHistory.close()

problem = StiffenedPanelOptimizationCS3()

algorithm = NSGA2(
    pop_size=3,
    n_offsprings=1,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.7, eta=40),
    mutation=PM(eta=50),
    eliminate_duplicates=True
)

from pymoo.termination import get_termination
termination = get_termination("n_gen", 2)

from pymoo.optimize import minimize
res = minimize(problem,
            algorithm,
            termination,
            seed=1,
            save_history=True,
            verbose=True)

F = res.F
X = res.X

print(X)
print("Program executed in: %s seconds" % (time.time() - start_time))

n_evals = np.array([e.evaluator.n_eval for e in res.history])
opt = np.array([e.opt[0].F for e in res.history])
variables = np.array([e.opt[0].X for e in res.history])

fig, ax1 = plt.subplots()
fig.suptitle("Stiffened Panel Optimization")
ax1.set_title("Mass vs. Evaluations")
ax1.set_xlabel("Generations")
ax1.set_ylabel("Mass")

ax1.scatter(n_evals, opt, s=10, facecolors='none', edgecolors='r', marker='.')
plt.show()