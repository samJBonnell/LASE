# We want to minimize mass with continous panel thickness, and ensure that NO point exceeds 175MPa of stress
# Define the set of variables that can exist and bounds (removed due to need to re-evaluate the limits set on each variable):
# 1.  Transverse Stiffener Number
# 2.  Longitudinal Stiffener Number
# 3.  Panel Thickness
# 4.  Transverse Stiffener Height
# 5.  Transverse Stiffener Thickness
# 6.  Transverse Flange Thickness
# 7.  Transverse Flange Width
# 8.  Longitudinal Stiffener Height
# 9.  Longitudinal Stiffener Thickness
# 10. Longitudinal Flange Thickness
# 11. Longitudinal Flange Width
# 12. Pressure Magnitude
# 13. Plate Mesh Size
# 14. Transverse Stiffener Mesh Size
# 15. Transverse Flange Mesh Size
# 16. Longitudinal Stiffener Mesh Size
# 17. Longitudinal Flange Mesh Size
# 18. Panel Width
# 19. Panel Length

# Further constraints exist due to the limiting description of the panel in ABAQUS:
# 1. Height of Transverse Stiffeners > Height of Longitudinal Stiffeners

# Python Imports
import numpy as np
import time
import subprocess
import matplotlib.pyplot as plt
from datetime import datetime

# Pymoo Imports
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination

# Self-Defined Libraries
import FiniteElementModel as FEM

# Remove a non-compilation warning 
from pymoo.config import Config
Config.warnings['not_compiled'] = False

date = datetime.today().strftime('%Y-%m-%d')
start_time = time.time()

# Model
input_keys = ["nTS", "nLS", "tP", "hTS", "tTS", "wTF", "tTF", "hLS", "tLS", "tLF", "wLF", "P", "mP", "mTS", "mTF", "mLS", "mLF", "W", "L"]
input_path = "temp/input.csv"

output_keys = ["sVM", "m"]
output_path = "temp/output.csv"

variables = FEM.load_extern('initial.csv') # Load an initial set of variables from an external source. The geometric information will be overwritten but mesh sizes, etc. will be preserved through the process.
variables = np.array(variables)
stiffened_panel = FEM.FiniteElementModel("StiffenedPanel.py", input_path, output_path, input_keys, output_keys)

# Optimization Parameters
Generations = 50
Population = 30
Offspring = 18

# NSGA-II Parameters
SBX_prob = 0.7
SBX_eta = 70
Mutation_PM = 60

# Notes
# comments = "Case Study 15- 75000 Pa Uniform Load"

# # Write variables to simulation information files
# output = open("temp\\information.txt", 'w')
# output.write(comments + "\n")
# output.write("Date: " + date + "\n")
# output.write("Start Time: " + str(start_time) + "\n")
# output.write("\n")
# output.write("Simulation Parameters\n")
# output.write("Pressure: " + str(Pressure) + " Pa" + "\n")
# output.write("\n")
# output.write("Optimization Parameters\n")
# output.write("Generations: " + str(Generations) + "\n")
# output.write("Population: " + str(Population) + "\n")
# output.write("Offspring: " + str(Offspring) + "\n")
# output.write("\n")
# output.write("NSGA-II Parameters\n")
# output.write("SBX Probability: " + str(SBX_prob) + "\n")
# output.write("SBX ETA: " + str(SBX_eta) + "\n")
# output.write("Mutation PM: " + str(Mutation_PM))
# output.close()

class StiffenedPanelOptimizationCS3(ElementwiseProblem):
    # Give access to meshsize and pressure for simulation
    global Pressure
    global PlateMesh
    global TransverseStiffenerMesh
    global TransverseFlangeMesh
    global LongitudinalStiffenerMesh
    global LongitudinalFlangeMesh
    global PanelWidth
    global PanelLength

    def __init__(self):
        super().__init__(n_var=11,
                         n_obj=1,
                         n_ieq_constr=2,
                         xl = np.array([1, 1, 0.005, 0.05, 0.005, 0.005, 0.010, 0.010, 0.005, 0.005, 0.010]),
                         xu = np.array([10, 10, 0.050, 1.00, 0.050, 0.050, 0.750, 0.950, 0.050, 0.050, 0.500]))

    def _evaluate(self, x, out, *args, **kwargs):
        # Create 'template' integer values for stiffener numbers
        x[0] = round(x[0], 0)
        x[1] = round(x[1], 0)

        if x[7] >= x[3]:
            x[7] = x[3] - 0.0001

        data = stiffened_panel.evaluate(x) # Evalute the objective function
        stress = data["output"][0]
        mass = data["output"][1]

        # The objective function is to minimze the mass of the panel
        f1 = mass
        
        # Constraints are defined by max stress & geometric tolerancing due to assignment in ABAQUS
        g1 = stress - 1.75e+8
        g2 = x[7] - x[3]

        out["F"] = [f1]
        out["G"] = [g1, g2]

        stiffened_panel.save("temp\\history.csv")

problem = StiffenedPanelOptimizationCS3()

algorithm = NSGA2(
    pop_size=Population,
    n_offsprings=Offspring,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=SBX_prob, eta=SBX_eta),
    mutation=PM(eta=Mutation_PM),
    eliminate_duplicates=True
)

print("\n--- Started Analysis ---\n")

best = []

termination = get_termination("n_gen", Generations)
algorithm.setup(problem, termination=termination, seed=None, verbose=False)

# Run the algorithm, printing the generations of each trial
while algorithm.has_next():
    algorithm.next()

    tempList = algorithm.pop.get("F")
    index_min = min(range(len(tempList)), key=tempList.__getitem__)
    best.append(algorithm.pop.get("X")[index_min])

    writeGens = open("temp\\generations.csv", 'a')
    writeGens.write(str(algorithm.n_gen - 1) + "," + str(algorithm.evaluator.n_eval) + "\n")
    writeGens.close()

res = algorithm.result()

print("\n\n!!! - Program executed in: %s hours" % round((time.time() - start_time)/3600, 3))

writeResults = open("temp\\results.csv", 'w')
for gen in best:
    writeResults.write(str(gen) + "\n")

writeResults.close()

print("\n--- Analysis Completed ---\n")

# Record elapsed run time
output = open("temp\\information.txt", 'a')
output.write("\n\nCompletion Time: " + str(time.time()) + "\n")
output.write("Elapsed Time: " + str((time.time() - start_time)/3600) + " hours")
output.close()