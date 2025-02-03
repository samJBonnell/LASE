resetFiles = ["abaqusOutput.csv", "generations.csv", "history.csv", "optimizationFile.csv", "information.txt", "results.csv"]

for file in resetFiles:
    tempFile = open("temp\\" + file, 'r+')
    
    tempFile.truncate(0)
    tempFile.close()

print("Optimization Files Reset!\n")