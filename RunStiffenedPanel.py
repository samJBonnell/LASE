# Python Imports
import subprocess

print("\n--- Started Analysis ---\n")

# Function call to the ABAQUS module & wait for function call to complete
functionCall = subprocess.Popen(["abaqus", "cae", "noGUI=StiffenedPanelPythonScript.py"], shell=True)
functionCall.communicate()

# Once the program is done running, 
with open("temp\\abaqusOutput.csv") as file:
    lines = [line.rstrip() for line in file]

# Remove the 'lines[2]' call for non-weld length defined panels
writeHistory = open("temp\\history.csv", 'a')
writeHistory.write(str(lines[0]) + "," + str(lines[1]) + "\n")
writeHistory.close()

print("\n--- Analysis Completed ---\n")