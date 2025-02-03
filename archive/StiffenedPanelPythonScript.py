# Program Information
# The following program is a parametric definiton of a stiffened panel allowing for the iteration of panel geometries and thicknesses for
# a variety of optimization problems. This was created to complete two of four optimization tasks in late 2024 as a learning opportunity
# prior to starting fully into 

# Sam Bonnell - UBC Labratory for Structural Efficiency MASc Student
# 2024-12-16

# ----------------------------------------------------------------------------------------------------------------------------------
# Operation Mode
# If operation mode is set to True, the program will pull panel dimensions from "temp\optimizationFile.csv" where the last line of the
# file represents the most recent iteration of the optmization.
# The variables, across a row, in "temp\optimizationFile.csv" are as follows:
#   1. Number of transverse stiffeners:    2 < x < 4
#   2. Number of longitudinal stiffeners:  2 < x < 7
#   3. Plate thickness:                    0.005 < x < 0.05
#   4. Transvers Stiffener Height:         0.050 < x < 1.00
#   5. Transverse Stiffener thickness:     0.005 < x < 0.05      
#   6. Transverse Flange thickness:        0.005 < x < 0.05
#   7. Transverse Flange width:            0.010 < x < 0.75
#   8. Longitudinal Stiffener Height:      0.010 < x < 0.95
#   9. Longitudinal Stiffener thickness:   0.005 < x < 0.05
#   10. Longitudinal Flange thickness:     0.005 < x < 0.05
#   11. Longitudinal Flange width:         0.010 < x < 0.50

# If operation mode is set to 'False', panel parameters will be pulled directly from the 'Design Parameter' section of this script

OPMODE = True
if OPMODE is True:
    with open("temp\\optimizationFile.csv", 'r') as f:
        generations = f.read().splitlines()
        newGen = generations[-1]
    
    panelVariables = newGen.split(',')

    # Macro Dimensions
    TransverseStiffenerNum = int(float(panelVariables[0]))
    LongitudinalStiffenerNum = int(float(panelVariables[1]))

    # Panel
    PanelThickness = float(panelVariables[2])

    # Transverse Regions
    TransverseStiffenerHeight = float(panelVariables[3])
    TransverseStiffenerThickness = float(panelVariables[4])
    TransverseFlangeThickness = float(panelVariables[5])
    TransverseFlangeWidth = float(panelVariables[6])

    # Longitudinal Regions
    LongitudinalStiffenerHeight = float(panelVariables[7])
    LongitudinalStiffenerThickness = float(panelVariables[8])
    LongitudinalFlangeThickness = float(panelVariables[9])
    LongitudinalFlangeWidth = float(panelVariables[10])

    # Simulation Parameters
    PressureMagnitude = float(panelVariables[11])
    MeshSize = float(panelVariables[12])

    PanelWidth = float(panelVariables[13])
    PanelLength = float(panelVariables[14])


# ----------------------------------------------------------------------------------------------------------------------------------
# Library Import
import numpy as np

# ----------------------------------------------------------------------------------------------------------------------------------
# Function Definitions

def createSurface(assembly, surfaceName, objectName, catchPoint):
    assembly.Surface(name=surfaceName, side2Faces=assembly.instances[objectName].faces.findAt((catchPoint,)))

def createSurfaceBounds(assembly, surfaceName, objectName, bounds):
    surf = assembly.instances[objectName].faces.getByBoundingBox(xMin=bounds[0], xMax=bounds[1], yMin=bounds[2], yMax=bounds[3], zMin=bounds[4], zMax=bounds[5])
    assembly.Surface(name=surfaceName, side2Faces=surf)

def assignSection(model, partName, secName, catchPoints):
    tempSurf = []
    for point in catchPoints:
        tempSurf.append(model.parts[partName].faces.findAt((point,)))
    setSurf = tempSurf[0]
    for index in range(1, len(tempSurf)):
        setSurf += tempSurf[index] 
    model.parts[partName].Set(faces=setSurf, name='sectionAssignment')
    model.parts[partName].SectionAssignment(
        offset=0.0, 
        offsetField='', 
        offsetType=MIDDLE_SURFACE, 
        region=model.parts[partName].sets['sectionAssignment'],
        sectionName=secName,
        thicknessAssignment=FROM_SECTION)

def assignSectionBounds(model, partName, secName, bounds):
    surfSet = model.parts[partName].faces.getByBoundingBox(xMin=bounds[0], xMax=bounds[1], yMin=bounds[2], yMax=bounds[3], zMin=bounds[4], zMax=bounds[5])
    model.parts[partName].Set(faces=surfSet, name='sectionAssignment')
    model.parts[partName].SectionAssignment(
        offset=0.0,
        offsetField='', 
        offsetType=MIDDLE_SURFACE, 
        region=model.parts[partName].sets['sectionAssignment'],
        sectionName=secName,
        thicknessAssignment=FROM_SECTION)

def createEdge(assembly, edgeName, objectName, catchPoint):
    assembly.Set(edges=assembly.instances[objectName].edges.findAt((catchPoint,)), name=edgeName)

def createEdgeBounds(assembly, edgeSetName, instanceName, bounds):
    edgeSet = assembly.instances[instanceName].edges.getByBoundingBox(xMin=bounds[0], xMax=bounds[1], yMin=bounds[2], yMax=bounds[3], zMin=bounds[4], zMax=bounds[5])
    assembly.Set(edges=edgeSet, name=edgeSetName)
    return edgeSet

def writeDebug(object):
    f = open("temp\\debug.csv", "w")
    f.write(str(object) + "\n")
    f.close()

# ----------------------------------------------------------------------------------------------------------------------------------
# Design Parameters

# ----------------------------------------------------------------------------------------------------------------------------------

if OPMODE is not True:
    # Global Dimensions of Panel
    PanelWidth = 3
    PanelLength = 6

    # Transverse Regions
    TransverseStiffenerNum = 2
    TransverseStiffenerHeight = 0.45
    TransverseFlangeWidth = 0.25

    # Longitudinal Regions
    LongitudinalStiffenerNum = 6
    LongitudinalStiffenerHeight = 0.4
    LongitudinalFlangeWidth = 0.175

    # ----------------------------------------------------------------------------------------------------------------------------------
    # Thickness Definitions
    PanelThickness = 0.020

    # Transverse Regions
    TransverseStiffenerThickness = 0.020
    TransverseFlangeThickness = 0.020

    # Longitudinal Regions
    LongitudinalStiffenerThickness = 0.010
    LongitudinalFlangeThickness = 0.010

    # Simulation Parameters
    PressureMagnitude = -10000
    MeshSize = 0.05

# Creation of a list used to create section assignments for each component of the panel
ThicknessList = []
ThicknessList.append(PanelThickness)

if TransverseStiffenerThickness not in ThicknessList:
    ThicknessList.append(TransverseStiffenerThickness)

if TransverseFlangeThickness not in ThicknessList:
    ThicknessList.append(TransverseFlangeThickness)

if LongitudinalStiffenerThickness not in ThicknessList:
    ThicknessList.append(LongitudinalStiffenerThickness)

if LongitudinalFlangeThickness not in ThicknessList:
    ThicknessList.append(LongitudinalFlangeThickness)

# ----------------------------------------------------------------------------------------------------------------------------------

# ABAQUS Prefactory Information
from abaqus import *
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)

# Import module information from ABAQUS
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import odbAccess

# Configure coordinate output
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

# ----------------------------------------------------------------------------------------------------------------------------------
# Start of Definition of Panel Model

# Create model object
model = mdb.Model(name='Model-1')

# Part Definitions
# Plate
model.Part(
    name='plate',
    dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)

# Transverse Stiffener
model.Part(
    name='transStiff',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

# Transverse Flange
model.Part(
    name='transFlange',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

# Longitudinal Stiffener
model.Part(
    name='longStiff',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

# Longitudinal Flange
model.Part(
    name='longFlange',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

# ----------------------------------------------------------------------------------------------------------------------------------
# Definition of Panel Model follows...
# Part Geometry

# Plate sketch & part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(-(float(PanelWidth)/2), 0), point2=(float(PanelWidth)/2, 0))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)

model.parts['plate'].BaseShellExtrude(depth=PanelLength, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# ----------------------------------------------------------------------------------------------------------------------------------
# Transverse Stiffener sketch & part
stepSize = 0
stiffenerPoint = -(float(PanelLength)/2)
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
for index in range(TransverseStiffenerNum):
    if index is 0:
        stepSize = float(PanelLength)/(2*TransverseStiffenerNum)
    else:
        stepSize = float(PanelLength)/(TransverseStiffenerNum)
    stiffenerPoint += stepSize
    model.sketches['profileSketch'].Line(point1=(stiffenerPoint, 0.0), point2=(stiffenerPoint, TransverseStiffenerHeight))
    model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[2 + index], addUndoState=False)

model.parts['transStiff'].BaseShellExtrude(depth=PanelWidth, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# ----------------------------------------------------------------------------------------------------------------------------------
# Transverse Flange sketch & part
halfWidth = float(TransverseFlangeWidth)/2

stepSize = 0
stiffenerPoint = -(float(PanelLength)/2)
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
for index in range(TransverseStiffenerNum):
    if index is 0:
        stepSize = float(PanelLength)/(2*TransverseStiffenerNum)
    else:
        stepSize = float(PanelLength)/(TransverseStiffenerNum)
    stiffenerPoint += stepSize
    model.sketches['profileSketch'].Line(point1=(stiffenerPoint - halfWidth, TransverseStiffenerHeight), point2=(stiffenerPoint + halfWidth, TransverseStiffenerHeight))
    model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2 + index], addUndoState=False)

model.parts['transFlange'].BaseShellExtrude(depth=PanelWidth, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# ----------------------------------------------------------------------------------------------------------------------------------
# Longitudinal Stiffener sketch & part
stepSize = 0
stiffenerPoint = -(float(PanelWidth)/2)
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
for index in range(LongitudinalStiffenerNum):
    stepSize = float(PanelWidth)/(LongitudinalStiffenerNum + 1)
    stiffenerPoint += stepSize
    model.sketches['profileSketch'].Line(point1=(stiffenerPoint, 0.0), point2=(stiffenerPoint, LongitudinalStiffenerHeight))
    model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[2 + index], addUndoState=False)

model.parts['longStiff'].BaseShellExtrude(depth=PanelLength, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# ----------------------------------------------------------------------------------------------------------------------------------
# Longitudinal Flange sketch & part
halfWidth = float(LongitudinalFlangeWidth)/2

stepSize = 0
stiffenerPoint = -(float(PanelWidth)/2)
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
for index in range(LongitudinalStiffenerNum):
    stepSize = float(PanelWidth)/(LongitudinalStiffenerNum + 1)
    stiffenerPoint += stepSize
    model.sketches['profileSketch'].Line(point1=(stiffenerPoint - halfWidth, LongitudinalStiffenerHeight), point2=(stiffenerPoint + halfWidth, LongitudinalStiffenerHeight))
    model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2 + index], addUndoState=False)

model.parts['longFlange'].BaseShellExtrude(depth=PanelLength, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# ----------------------------------------------------------------------------------------------------------------------------------
# Material & Section Definitions
model.Material(name='steel')
model.materials['steel'].Elastic(table=((200000000000.0,0.3),))
model.materials['steel'].Density(table=((7850,float(296.15)),))

# Section Defintions
for index in range(len(ThicknessList)):
    model.HomogeneousShellSection(
    idealization=NO_IDEALIZATION,
    integrationRule=SIMPSON,
    material='steel',
    name='t-' + str(ThicknessList[index]),
    nodalThicknessField='',
    numIntPts=5,
    poissonDefinition=DEFAULT,
    preIntegrate=OFF,
    temperature=GRADIENT,
    thickness=0.01,
    thicknessField='',
    thicknessModulus=None, 
    thicknessType=UNIFORM, 
    useDensity=OFF)

# ----------------------------------------------------------------------------------------------------------------------------------

# Assembly & Instances
model.rootAssembly.DatumCsysByDefault(CARTESIAN)
assembly = model.rootAssembly

# Create Step Object
model.StaticStep(name='Step-1', previous='Initial')

# Instance Creation
assembly.Instance(dependent=ON, name='plate-1', part=model.parts['plate'])
assembly.Instance(dependent=ON, name='transStiff-1', part=model.parts['transStiff'])
assembly.Instance(dependent=ON, name='transFlange-1', part=model.parts['transFlange'])
assembly.Instance(dependent=ON, name='longStiff-1', part=model.parts['longStiff'])
assembly.Instance(dependent=ON, name='longFlange-1', part=model.parts['longFlange'])

# Instance Transformations
assembly.rotate(instanceList=['transStiff-1', 'transFlange-1'], axisPoint=(0.0,0.0,float(PanelWidth)/2), axisDirection=(0.0,1.0,0.0), angle=-90)
assembly.translate(instanceList=['plate-1','longStiff-1','longFlange-1'], vector=(0.0,0.0,-float(PanelLength)/2))
assembly.translate(instanceList=['transStiff-1', 'transFlange-1'], vector=(0.0,0.0,-float(PanelWidth)/2))

assembly.InstanceFromBooleanCut(name='longStiff', instanceToBeCut=assembly.instances['longStiff-1'], cuttingInstances=[assembly.instances['transStiff-1']])
assembly.resumeFeatures(featureNames=['transStiff-1'])

assembly.InstanceFromBooleanCut(name='longFlange', instanceToBeCut=assembly.instances['longFlange-1'], cuttingInstances=[assembly.instances['transStiff-1']])
assembly.resumeFeatures(featureNames=['transStiff-1'])

# Section Assignment
boundingLength = max(PanelLength, PanelWidth, TransverseStiffenerHeight, LongitudinalStiffenerHeight)

# Needs to be completed after the boolean operations to ensure that the section assignment is applied to the newly created sections
assignSectionBounds(model, 'plate', 't-' + str(PanelThickness), [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'transStiff', 't-' + str(TransverseStiffenerThickness), [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'transFlange', 't-' + str(TransverseFlangeThickness), [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'longStiff', 't-' + str(LongitudinalStiffenerThickness), [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'longFlange', 't-' + str(LongitudinalFlangeThickness), [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])

# ----------------------------------------------------------------------------------------------------------------------------------
# Creation of surface and edge indexing to allow constraint creation parametrically!

surfaceList = ['plate-1', 'longFlange-2', 'transFlange-1']
for index in range(TransverseStiffenerNum):
    surfaceList.append('transStiff-1')

# Plate, Longitudinal Flange, Longitudinal Stiffeners @ each Transverse Stiffeners
edgeList = ['longStiff-2', 'longStiff-2']
for index in range(TransverseStiffenerNum):
    edgeList.append('longStiff-2')

for index in range(TransverseStiffenerNum):
    edgeList.append('longFlange-2')

edgeList.append('transStiff-1')
edgeList.append('transStiff-1')

# Bounding boxes used to identify edges for constraints
tOffset = 0.01
bounds = [
    [-float(PanelWidth)/2, float(PanelWidth)/2, -tOffset, tOffset, -float(PanelLength)/2, float(PanelLength)/2],
    [-float(PanelWidth)/2, float(PanelWidth)/2, float(LongitudinalStiffenerHeight) - tOffset, float(LongitudinalStiffenerHeight) + tOffset, -float(PanelLength)/2, float(PanelLength)/2],
    [-float(PanelWidth)/2, float(PanelWidth)/2, float(TransverseStiffenerHeight) - tOffset, float(TransverseStiffenerHeight) + tOffset, -float(PanelLength)/2, float(PanelLength)/2]
    ]

stepSize = 0
stiffenerPoint = -(float(PanelLength)/2)
for index in range(TransverseStiffenerNum):
    if index is 0:
        stepSize = float(PanelLength)/(2*TransverseStiffenerNum)
    else:
        stepSize = float(PanelLength)/(TransverseStiffenerNum)
    stiffenerPoint += stepSize
    bounds.append([-float(PanelWidth)/2, float(PanelWidth)/2, -tOffset, TransverseStiffenerHeight + tOffset, stiffenerPoint - tOffset, stiffenerPoint + tOffset])

# Creating searchable indexes for each of the parts
surfaceIndex = [0, 1, 2]
for index in range(TransverseStiffenerNum):
    surfaceIndex.append(3 + index)

edgeIndex = [0, 1]
for index in range(2):
    for edges in range(TransverseStiffenerNum):
        edgeIndex.append(3 + edges)

edgeIndex.append(0)
edgeIndex.append(2)

constraintIndex = edgeIndex

# Creating sets of constraint edges and surfaces based on the parts and indexing completed above
for i in range(len(surfaceList)):
    createSurfaceBounds(assembly, 'surf-' + str(i), surfaceList[i], bounds[surfaceIndex[i]])

for i in range(len(edgeList)):
    createEdgeBounds(assembly, 'edge-' + str(i), edgeList[i], bounds[edgeIndex[i]])

for i in range(len(constraintIndex)):
    model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-' + str(constraintIndex[i])],
    name='Constraint' + str(i),
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edge-' + str(i)],
    thickness=ON,
    tieRotations=ON)

# --------------------------------------------------------------------------------------------------------------------------------------------
# Boundary Conditions

tOffset = 0.01
boundaryRegions = [
    # X-Aligned BCs
    [float(PanelWidth)/2 - tOffset, float(PanelWidth)/2 + tOffset, -tOffset, TransverseStiffenerHeight + tOffset, -float(PanelLength)/2, float(PanelLength)/2],
    [-float(PanelWidth)/2 - tOffset, -float(PanelWidth)/2 + tOffset, -tOffset, TransverseStiffenerHeight + tOffset, -float(PanelLength)/2, float(PanelLength)/2],
        
    # Z-Aligned BCs
    [-float(PanelWidth)/2, float(PanelWidth)/2, -tOffset, TransverseStiffenerHeight + tOffset, float(PanelLength)/2 - tOffset, float(PanelLength)/2 + tOffset],
    [-float(PanelWidth)/2, float(PanelWidth)/2, -tOffset, TransverseStiffenerHeight + tOffset, -float(PanelLength)/2 - tOffset, -float(PanelLength)/2 + tOffset]
    ]

boundaryList = [
    ['transFlange-1', 'transStiff-1', 'plate-1'],
    ['longFlange-2', 'longStiff-2', 'plate-1']
    ]

e1 = createEdgeBounds(assembly, 'TempSet-1', boundaryList[0][0], boundaryRegions[0])
e2 = createEdgeBounds(assembly, 'TempSet-2', boundaryList[0][1], boundaryRegions[0])
e3 = createEdgeBounds(assembly, 'TempSet-3', boundaryList[0][2], boundaryRegions[0])
e4 = createEdgeBounds(assembly, 'TempSet-4', boundaryList[0][0], boundaryRegions[1])
e5 = createEdgeBounds(assembly, 'TempSet-5', boundaryList[0][1], boundaryRegions[1])
e6 = createEdgeBounds(assembly, 'TempSet-6', boundaryList[0][2], boundaryRegions[1])

tempSet = e1 + e2 + e3 + e4 + e5 + e6
assembly.Set(edges=tempSet, name='BCs-1')

e1 = createEdgeBounds(assembly, 'TempSet-1', boundaryList[1][0], boundaryRegions[2])
e2 = createEdgeBounds(assembly, 'TempSet-2', boundaryList[1][1], boundaryRegions[2])
e3 = createEdgeBounds(assembly, 'TempSet-3', boundaryList[1][2], boundaryRegions[2])
e4 = createEdgeBounds(assembly, 'TempSet-4', boundaryList[1][0], boundaryRegions[3])
e5 = createEdgeBounds(assembly, 'TempSet-5', boundaryList[1][1], boundaryRegions[3])
e6 = createEdgeBounds(assembly, 'TempSet-6', boundaryList[1][2], boundaryRegions[3])

tempSet = e1 + e2 + e3 + e4 + e5 + e6
assembly.Set(edges=tempSet, name='BCs-2')

# Create displacement boundary conditions and apply a pressure to the whole assembly
model.DisplacementBC(amplitude=UNSET, createStepName='Step-1',distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='BC-1', region=assembly.sets['BCs-1'], u1=0.0,u2=0.0, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0)
model.DisplacementBC(amplitude=UNSET, createStepName='Step-1',distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='BC-2', region=assembly.sets['BCs-2'], u1=0.0, ur1=0.0)

model.Pressure(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, field='', magnitude=float(PressureMagnitude), name='Load-1', region=assembly.surfaces['surf-0'])

# Meshing the Part
# Seed part mesh and generate mesh for each part
model.parts['plate'].seedPart(deviationFactor=0.1,minSizeFactor=0.1, size=MeshSize)
model.parts['plate'].generateMesh()

model.parts['transStiff'].seedPart(deviationFactor=0.1,minSizeFactor=0.1, size=MeshSize)
model.parts['transStiff'].generateMesh()

model.parts['transFlange'].seedPart(deviationFactor=0.1,minSizeFactor=0.1, size=MeshSize)
model.parts['transFlange'].generateMesh()

model.parts['longStiff'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=MeshSize)
model.parts['longStiff'].generateMesh()

model.parts['longFlange'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=MeshSize)
model.parts['longFlange'].generateMesh()

# ----------------------------------------------------------------------------------------------------------------------------------
# Create Job

mdb.Job(atTime=None,
        contactPrint=OFF,
        description='',
        echoPrint=OFF,
        explicitPrecision=SINGLE,
        getMemoryFromAnalysis=True,
        historyPrint=OFF,
        memory=90,
        memoryUnits=PERCENTAGE,
        model='Model-1',
        modelPrint=OFF,
        multiprocessingMode=DEFAULT, 
        name='Job-' + str(0),
        nodalOutputPrecision=SINGLE,
        numCpus=1,
        numGPUs=0,
        queue=None,
        resultsFormat=ODB,
        scratch='',
        type=ANALYSIS,
        userSubroutine='',
        waitHours=0,
        waitMinutes=0)

# Submit job and wait for completion

mdb.jobs['Job-' + str(0)].submit(consistencyChecking=OFF)
mdb.jobs['Job-' + str(0)].waitForCompletion()

# # ----------------------------------------------------------------------------------------------------------------------------------
# # Write the mass and highest stress to an output file

odb_path = r"Z:\development\script\\Job-" + str(0) + ".odb"
odb = odbAccess.openOdb(path=odb_path, readOnly=True)

stressTensor = odb.steps['Step-1'].frames[-1].fieldOutputs['S'].getSubset(position=INTEGRATION_POINT)
vonMisesStress = stressTensor.getScalarField(invariant=MISES)

maxVonMisesStress = 0
for index in range(len(vonMisesStress.bulkDataBlocks)):
    tempStressArray = vonMisesStress.bulkDataBlocks[index]
    tempStress = np.max(tempStressArray.data)
    maxVonMisesStress = tempStress if tempStress > maxVonMisesStress else maxVonMisesStress

assemblyMass = assembly.getMassProperties()['mass']

f = open("temp\\abaqusOutput.csv", "w")
f.write(str(maxVonMisesStress) + "\n" + str(assemblyMass))
f.close()