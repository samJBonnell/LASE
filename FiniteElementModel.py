import numpy as np
import subprocess

class FiniteElementModel:
    def __init__(self, model, input_path, output_path, input_keys, output_keys): # model program name, output file name, variableKeys, input file name, resultKeys
        # Define the model that will be run by the program
        self.model = model

        # Define the output file name
        self.input_path = input_path
        self.input_keys = input_keys
        self.input = np.zeros(len(input_keys))

        # Define the results we expect to recieve from the model
        self.output_path = output_path
        self.output_keys = output_keys
        self.output = np.zeros(len(output_keys))

        # Define a history to store previous information about the system
        self.history = []

        # Initialize the state dictionary to store input/output data and execution status
        self.state = {
            "inputs": self.input,
            "outputs": self.output,
            "previous_states": []
        }
        self.status = "uninitialized"

    def update_input(self, input):
        """Updates input variables without modifying stored values."""
        self.input = input

    def backup(self):
        """Stores previous inputs/outputs before modification."""
        self.history.append({
            "input": self.input.copy(),
            "output": self.output.copy()
        })

    def write(self):
        """Writes current inputs to the input file."""
        # Write the variables to the disk to be passed to the ABAQUS model
        input = ""
        for index in range(len(self.input_keys)):
            input += str(self.input[index])
            if index != len(self.input) - 1:
                input += ","

        input += '\n'

        writer = open(self.input_path, 'a')
        writer.write(input)
        writer.close()

    def run(self):
        """Executes the FEM model."""
        try:
            with open("abaqus_log.txt", "w") as log_file:
                functionCall = subprocess.Popen(["abaqus", "cae", f"noGUI={self.model}"],
                    stdout=log_file,
                    stderr=log_file,
                    shell=True
                    )
            # functionCall = subprocess.Popen(["python3"], shell=True)
            # functionCall = subprocess.Popen(["abaqus", "cae", f"noGUI={self.model}"], shell=True)
            functionCall.communicate()
            self.status = "success"
        except Exception as e:
            self.status = f"failed: {e}"

    def read(self):
        """Reads FEM output and updates internal state."""
        if self.status == "success":
            with open(self.output_path) as file:
                lines = [line.rstrip() for line in file]

            # Need to ensure that the order of the variables is the same as for the input and output of the self
            for index in range(0,len(self.output_keys)):
                self.output[index] = float(lines[index])
        else:
            raise RuntimeError("Cannot read output: Model execution failed.")

    def evaluate(self, *args):
        """Runs FEM model and reads results."""
        if len(args) > 0:
            self.update_input(args[0])
        self.write()
        self.run()
        self.read()
        self.backup()

        return self.return_history()

    def return_history(self, n=1):
        """Returns last 'n' stored states."""
        return self.history[-n:][0]
    
    def save(self, file_path, *args):
        """Saves inputs/outputs to a file (optional)."""
        output = open(file_path, 'a')
        # Save results every time we call this function
        for index in range(len(self.output_keys)):
            output.write(str(self.output[index]) + ',')

        # Save variables only if we supply a variable argument to the function
        if args:
            for index in range(len(self.input_keys)):
                output.write(str(self.input[index]) + ',')

        # Write a closing bit at the end of the file to allow for future additions
        output.write("\n")
        output.close()

def load_extern(input_path):
    with open(input_path, 'r') as f:
        temp = f.read().splitlines() # Capture the final row of the input file
        temp = temp[-1]
    
    temp = temp.split(',')
    temp = [float(x) for x in temp]
    
    return temp