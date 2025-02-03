# This file is used to run the sensitivity analysis of the model

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

# Python Inserts
import numpy as np
import time
import subprocess
import matplotlib.pyplot as plt
from datetime import datetime

# Title of Sensitivity Analysis
title = "Plate Sensitivity Analysis"

# Date Information
date = datetime.today().strftime('%Y-%m-%d')
start_time = time.time()

# Mesh Size Parameters
fixedMesh = 0.01

# The variables here are either set to a temporary value or to a fixed value. The fixed value is recorded to a file for record.
PlateMesh = 0.00
TransverseStiffenerMesh = fixedMesh
TransverseFlangeMesh = fixedMesh
LongitudinalStiffenerMesh = fixedMesh
LongitudinalFlangeMesh = fixedMesh

# Write variables to simulation information files
output = open("temp\\information.txt", 'w')
output.write(title + "\n")
output.write("Date: " + date + "\n")
output.write("Start Time: " + str(start_time) + "\n")
output.write("\n")
output.write("Simulation Parameters\n")
output.write("Flange/Web Mesh Size: " + str(fixedMesh) + "\n")
output.close()

# Define range over which to evaluate the variable mesh size
MaxMesh = 0.5
tempMesh = 0.005

# Increment of mesh size during analysis
increment = 0.02

print("\n--- Started Analysis ---\n")

while tempMesh <= MaxMesh + increment:
    PlateMesh = tempMesh
    PanelVariables = [7.0,5.0,0.03325799359624334,0.4480278213012448,0.047241486394380194,0.028605970901913257,0.07560495367168495,0.10174021508604895,0.023672879650233524,0.023396059305756126,0.010043630612399454, -150000, PlateMesh, TransverseStiffenerMesh, TransverseFlangeMesh, LongitudinalStiffenerMesh, LongitudinalFlangeMesh, 3, 6]
    outputData = ""
    for index in range(len(PanelVariables)):
        outputData += str(PanelVariables[index]) + ","
    outputData += "\n"

    # Write PanelVariables into the temporary file to be used by ABAQUS
    output = open("temp\\optimizationFile.csv", 'a')
    output.write(outputData)
    output.close()

    # Function call to the ABAQUS module & wait for function call to complete
    functionCall = subprocess.Popen(["abaqus", "cae", "noGUI=StiffenedPanelPythonScript.py"], shell=True)
    functionCall.communicate()

    # Once the program is done running, 
    with open("temp\\abaqusOutput.csv") as file:
        lines = [line.rstrip() for line in file]

    # Append 
    output = open("temp\\results.csv", 'a')
    output.write(str(tempMesh) + ", " + str(lines[0]) + "\n")
    output.close()

    tempMesh += increment
    index += 1

# Record elapsed run time
output = open("temp\\information.txt", 'a')
output.write("\n\nCompletion Time: " + str(time.time()) + "\n")
output.write("Elapsed Time: " + str((time.time() - start_time)/3600) + " hours")
output.close()

print("\n--- Analysis Completed ---\n")