import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

class Viewer:
    def __init__(self, trial) -> None:
        generationFile = False
        resultsFile = False
        self.variablesMode = True

        self.trial = trial

        self.evaluations = []
        self.generations = []
        self.mass = []
        self.stress = []
        self.weldLength = []
        self.results = []
        self.variables = []

        my_file = Path("data/" + trial + "/generations.csv")
        if my_file.is_file():
            generationFile = True

        my_file = Path("data/" + trial + "/results.csv")
        if my_file.is_file():
            resultsFile = True

        with open("data/" + trial + "/history.csv") as file:
            temp = [line.rstrip() for line in file]
            for line in temp:
                temp = line.split(',')
                self.mass.append(float(temp[1]))
                self.stress.append(float(temp[0]))
                if (len(temp)) > 2:
                    self.weldLength.append(float(temp[2]))

        if generationFile is True:
            with open("data/" + trial + "/generations.csv") as file:
                self.inpGenerations = [line.rstrip() for line in file]

        if resultsFile is True:
            with open("data/" + trial + "/results.csv") as file:
                self.results = [float(line.rstrip()) for line in file]

        with open("data/" + self.trial + "/optimizationFile.csv") as file:
            temp = [line.rstrip() for line in file]
            for line in temp:
                self.variables.append(line.split(','))

        if (len(self.variables[-1]) >= 11):
            self.variablesMode = False

        if generationFile is True:
            previousIndex = 0
            for line in self.inpGenerations:
                temp = line.split(',')
                offSet = float(temp[1]) - previousIndex
                set = np.full(shape=int(offSet), fill_value=int(temp[0]))
                for gen in set:
                    self.generations.append(gen)
                previousIndex = float(temp[1])

            self.mass = self.mass[0:len(self.generations)]
            self.stress = self.stress[0:len(self.generations)]
            self.results = self.results[0:len(self.generations)]
            self.weldLength = self.weldLength[0:len(self.generations)]
            self.variables = self.variables[0:len(self.generations)]

        self.evaluations = range(1,len(self.mass) + 1)
    
    def data(self) -> list:
        return [self.evaluations, self.generations, self.mass, self.stress, self.weldLength, self.results, self.variables]