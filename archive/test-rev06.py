# This program is the same as rev05 but is parameterized to allow for creation of 'novel' panel structures
# Program 07 will allow variable assignment of material structures

# Program Information
# This program is used as a baseline for defining an entire stiffened panel structure and is NOT parameterized to allow for
# iteration once completed, this program will be used as a baseline to allow for the parameterization of the panel to allow 
# for optimization of the structure.

# Sam Bonnell - UBC LASE MASc Student
# 2024-11-30

# ---------------------------------------------------------------------------------------------------------------------------------

# The plate is 3 x 6 metres
# The tranverse stiffeners/flanges are spaced along the long plate axis at: 1.5 & 4.5 metres from the origin
# The longitudinal stiffeners/flanges are spaced along the short plate axis at: 0.75, 1.5, and 2.25 metres from the origin
# Longitudinal and transverse flanges are attached to the top height of their respective stiffeners

# Part sketches should all use the 'profileSketch' object which is to be deleted between part geometry construction

# Tasks:
# Parametrize the model to allow for creation of 'novel' panel structures

# ----------------------------------------------------------------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------------------------------------------------------------
# Design Parameters

PanelWidth = 3
PanelLength = 6

# Transverse Regions
TransverseStiffenerNum = 3
TransverseStiffenerHeight = 0.45
TransverseFlangeWidth = 0.25

# Longitudinal Regions
LongitudinalStiffenerNum = 4
LongitudinalStiffenerHeight = 0.4
LongitudinalFlangeWidth = 0.175

# Thicknesses (To be added in Rev07)

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

# Configure coordinate output
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

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

# Part Geometry Construction
# Plate sketch & part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(-(float(PanelWidth)/2), 0), point2=(float(PanelWidth)/2, 0))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)

model.parts['plate'].BaseShellExtrude(depth=PanelLength, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# ----------------------------------------------------------------------------------------------------------------------------------
# Transverse Stiffener sketch & part
# Requires a 'for loop' to allow for the creation of a variable number of panels
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

# Section Defintions
model.HomogeneousShellSection(
    idealization=NO_IDEALIZATION,
    integrationRule=SIMPSON,
    material='steel',
    name='plate-0010',
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
assignSectionBounds(model, 'plate', 'plate-0010', [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'transStiff', 'plate-0010', [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'transFlange', 'plate-0010', [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'longStiff', 'plate-0010', [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])
assignSectionBounds(model, 'longFlange', 'plate-0010', [-boundingLength, boundingLength, -boundingLength, boundingLength, -boundingLength, boundingLength])

# ----------------------------------------------------------------------------------------------------------------------------------
# Need to create surface and edge list from the number of stiffeners, etc.
# This is going to suck!
# Only ever three checks for the horizontal planes!

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
# The final piece required prior to creating a "completely" parametric codebase for the generation of variable panels (without the inclusion of thicknesses (yet))
# The boundary conditions are not changed based on the number of stiffeners, etc, thus, we can simply parameterize the boundary points themselves and go on our merry way!

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
model.DisplacementBC(amplitude=UNSET, createStepName='Step-1',distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name='BC-2', region=assembly.sets['BCs-2'], u1=0.0, ur2=0.0)

model.Pressure(amplitude=UNSET, createStepName='Step-1', distributionType=UNIFORM, field='', magnitude=float(-10000.0), name='Load-1', region=assembly.surfaces['surf-0'])

# Meshing the Part
# Seed part mesh and generate mesh for each part
model.parts['plate'].seedPart(deviationFactor=0.1,minSizeFactor=0.1, size=0.1)
model.parts['plate'].generateMesh()

model.parts['transStiff'].seedPart(deviationFactor=0.1,minSizeFactor=0.1, size=0.1)
model.parts['transStiff'].generateMesh()

model.parts['transFlange'].seedPart(deviationFactor=0.1,minSizeFactor=0.1, size=0.1)
model.parts['transFlange'].generateMesh()

model.parts['longStiff'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=0.1)
model.parts['longStiff'].generateMesh()

model.parts['longFlange'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=0.1)
model.parts['longFlange'].generateMesh()

# Create & Submit Job
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

mdb.jobs['Job-' + str(0)].submit(consistencyChecking=OFF)