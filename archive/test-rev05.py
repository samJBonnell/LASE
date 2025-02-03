# This program is the same as rev04 but uses for loops and some higher better file management to handle the large number of constraints

# Program Information
# This program is used as a baseline for defining an entire stiffened panel structure and is NOT parameterized to allow for
# iteration once completed, this program will be used as a baseline to allow for the parameterization of the panel to allow 
# for optimization of the structure.

# Sam Bonnell - UBC LASE MASc Student
# 2024-11-30

# ---------------------------------------------------------------------------------------------------------------------------------

# Notes
# 1. Create parts
# 2. Define part
#       - Geometry
#       - Internal sets and faces
# 3. Define materials
# 4. Define sections and assign to parts
# 5. Create assembly and instance parts
#       - Translation
#       - Rotation
# 6. Create a step in the simulation
# 7. Assign constraints and BCs
# 8. Unsure for now...

# Try to contain all sets relative to constraints as part level sets.
# Naming conventions
# Part Level Sets
#   - Feature-Location
#   Ex. Edge-Bottom
#       Edge-Side1
#       Face-Front
# 
# Instance Level Sets
#   - Joint-Name
#   Ex. Stiffener-Plate

# Panel consists of:
# - One (1) x panel
# - Two (2) x transverse stiffener
# - Nine (9) x longitudinal stiffener
# - Two (2) x transverse flange
# - Nine (9) x longitudinal flange

# The plate is 3 x 6 metres
# The tranverse stiffeners/flanges are spaced along the long plate axis at: 1.5 & 4.5 metres from the origin
# The longitudinal stiffeners/flanges are spaced along the short plate axis at: 0.75, 1.5, and 2.25 metres from the origin
# Longitudinal and transverse flanges are attached to the top height of their respective stiffeners

# Part sketches should all use the 'profileSketch' object which is to be deleted between part geometry construction

# Tasks:
# - Add BCs and loads
# - Run the simulation
# - Add a log of all locations that intersect and collect them into a set
#       - Instance level as the boolean operations will create new lines from single entities

# Re-write of test-rev04 to function based on bounding boxes instead of catchPoints and edges

# ----------------------------------------------------------------------------------------------------------------------------------

def createSurface(assembly, surfaceName, objectName, catchPoint):
    assembly.Surface(name=surfaceName, side2Faces=assembly.instances[objectName].faces.findAt((catchPoint,)))

def createSurfaceBounds(assembly, surfaceName, objectName, bounds):
    surf = assembly.instances[objectName].faces.getByBoundingBox(xMin=bounds[0], xMax=bounds[1], yMin=bounds[2], yMax=bounds[3], zMin=bounds[4], zMax=bounds[5])
    assembly.Surface(name=surfaceName, side2Faces=surf)

# assembly.instances['plate-1'].faces.getByBoundingBox(xMin=-1.5, xMax=1.5, yMin=-0.01, yMax=0.01, zMin=-3, zMax=3)
# [-1.5, 1.5, -0.01, 0.01, -3, 3]

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

# edgeSet = assembly.instances['longStiff-2'].edges.getByBoundingBox(xMin=-1.5, xMax=1.5, yMin=-0.01, yMax=0.01, zMin=0.74, zMax=0.76)
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
model.sketches['profileSketch'].Line(point1=(-1.5, 0), point2=(1.5, 0))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)

model.parts['plate'].BaseShellExtrude(depth=6.0, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# Transverse Stiffener sketch & part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(-1.5, 0.0), point2=(-1.5, 0.9))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(1.5, 0.0), point2=(1.5, 0.9))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[3], addUndoState=False)

model.parts['transStiff'].BaseShellExtrude(depth=3.0, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# Transverse Flange sketch & part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(-1.6, 0.9), point2=(-1.4, 0.9))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(1.4, 0.9), point2=(1.6, 0.9))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[3], addUndoState=False)

model.parts['transFlange'].BaseShellExtrude(depth=3.0, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# Longitudinal Stiffener sketch & part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(0.0, 0.0), point2=(0.0, 0.5))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(-0.75, 0.0), point2=(-0.75, 0.5))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[3], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(0.75, 0.0), point2=(0.75, 0.5))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[4], addUndoState=False)

model.parts['longStiff'].BaseShellExtrude(depth=6.0, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# Longitudinal Flange sketch & part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(-0.1, 0.5), point2=(0.1, 0.5))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(-0.85, 0.5), point2=(-0.65, 0.5))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[3], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(0.65, 0.5), point2=(0.85, 0.5))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[4], addUndoState=False)

model.parts['longFlange'].BaseShellExtrude(depth=6.0, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

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
assembly.rotate(instanceList=['transStiff-1', 'transFlange-1'], axisPoint=(0.0,0.0,1.5), axisDirection=(0.0,1.0,0.0), angle=-90)
assembly.translate(instanceList=['plate-1','longStiff-1','longFlange-1'], vector=(0.0,0.0,-3.0))
assembly.translate(instanceList=['transStiff-1', 'transFlange-1'], vector=(0.0,0.0,-1.5))

assembly.InstanceFromBooleanCut(name='longStiff', instanceToBeCut=assembly.instances['longStiff-1'], cuttingInstances=[assembly.instances['transStiff-1']])
assembly.resumeFeatures(featureNames=['transStiff-1'])

assembly.InstanceFromBooleanCut(name='longFlange', instanceToBeCut=assembly.instances['longFlange-1'], cuttingInstances=[assembly.instances['transStiff-1']])
assembly.resumeFeatures(featureNames=['transStiff-1'])

# Section Assignment
# Needs to be completed after the boolean operations to ensure that the section assignment is applied to the newly created sections
assignSectionBounds(model, 'plate', 'plate-0010', [-6, 6, -0.01, 1.6, -6, 6])
assignSectionBounds(model, 'transStiff', 'plate-0010', [-6, 6, -0.01, 1.6, -6, 6])
assignSectionBounds(model, 'transFlange', 'plate-0010', [-6, 6, -0.01, 1.6, -6, 6])
assignSectionBounds(model, 'longStiff', 'plate-0010', [-6, 6, -0.01, 1.6, -6, 6])
assignSectionBounds(model, 'longFlange', 'plate-0010', [-6, 6, -0.01, 1.6, -6, 6])

# ----------------------------------------------------------------------------------------------------------------------------------

# Contact Surfaces
# Planes that define contact pairs within the part
# Set Names:
# plate
#   One (1) x locations:
#   (0, 0, 0)
# assembly.Surface(name='surf-plate', side2Faces=assembly.instances['plate-1'].faces.findAt(((0, 0, 0),)))

# Rewrite of the contacts using bounding boxes to reduce the number of function calls and information stored
# Create surfaces by capturing them via bounding box - this becomes the same bounding box used to capture the edges to create the TIE constraints

# Requires knowing the number of individual constraints we need to create!

# Horizontal Constraints
# longStiff to plate
# longStiff to longFlange
# transStiff to plate
# transStiff to transFlange

# Vertical Constraints
# longStiff to transStiff
# longFlange to transStiff

surfPartListN = [
    # Horizontal Planes
    'plate-1',
    'longFlange-2',
    'transFlange-1',

    # Vertical Planes
    'transStiff-1',
    'transStiff-1'
    ]

edgePartListN = [
    # Plate
    'longStiff-2',

    # longFlange
    'longStiff-2',

    # transStiff
    'longStiff-2',
    'longStiff-2',

    # transStiff
    'longFlange-2',
    'longFlange-2',

    # Plate
    'transStiff-1',

    # transFlange
    'transStiff-1'
    ]

bounds = [
    [-1.5, 1.5, -0.01, 0.01, -3, 3], 
    [-1.5, 1.5, 0.49, 0.51, -3, 3],
    [-1.5, 1.5, 0.89, 0.91, -3, 3],
    [-1.5, 1.5, -0.01, 1.6, 1.4, 1.6],
    [-1.5, 1.5, -0.01, 1.6, -1.6, -1.4]
    ]

surfBoundsIndex = [0, 1, 2, 3, 4]
edgeBoundsIndex = [0, 1, 3, 4, 3, 4, 0, 2]
constraintIndex = [0, 1, 3, 4, 3, 4, 0, 2]

# plate
for i in range(len(surfPartListN)):
    createSurfaceBounds(assembly, 'surf-' + str(i), surfPartListN[i], bounds[surfBoundsIndex[i]])

for i in range(len(edgePartListN)):
    createEdgeBounds(assembly, 'edge-' + str(i), edgePartListN[i], bounds[edgeBoundsIndex[i]])

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

boundaryBounds = [
    # X-Aligned BCs
    [1.4, 1.6, -0.01, 1.6, -3, 3],
    [-1.6, -1.4, -0.01, 1.6, -3, 3],
        
    # Z-Aligned BCs
    [-1.5, 1.5, -0.01, 1.6, 2.9, 3.1],
    [-1.5, 1.5, -0.01, 1.6, -3.1, -2.9]
    ]

boundaryList = [
    ['transFlange-1', 'transStiff-1', 'plate-1'],
    ['longFlange-2', 'longStiff-2', 'plate-1']
    ]

e1 = createEdgeBounds(assembly, 'TempSet-1', boundaryList[0][0], boundaryBounds[0])
e2 = createEdgeBounds(assembly, 'TempSet-2', boundaryList[0][1], boundaryBounds[0])
e3 = createEdgeBounds(assembly, 'TempSet-3', boundaryList[0][2], boundaryBounds[0])
e4 = createEdgeBounds(assembly, 'TempSet-4', boundaryList[0][0], boundaryBounds[1])
e5 = createEdgeBounds(assembly, 'TempSet-5', boundaryList[0][1], boundaryBounds[1])
e6 = createEdgeBounds(assembly, 'TempSet-6', boundaryList[0][2], boundaryBounds[1])

tempSet = e1 + e2 + e3 + e4 + e5 + e6
assembly.Set(edges=tempSet, name='BCs-1')

e1 = createEdgeBounds(assembly, 'TempSet-1', boundaryList[1][0], boundaryBounds[2])
e2 = createEdgeBounds(assembly, 'TempSet-2', boundaryList[1][1], boundaryBounds[2])
e3 = createEdgeBounds(assembly, 'TempSet-3', boundaryList[1][2], boundaryBounds[2])
e4 = createEdgeBounds(assembly, 'TempSet-4', boundaryList[1][0], boundaryBounds[3])
e5 = createEdgeBounds(assembly, 'TempSet-5', boundaryList[1][1], boundaryBounds[3])
e6 = createEdgeBounds(assembly, 'TempSet-6', boundaryList[1][2], boundaryBounds[3])

tempSet = e1 + e2 + e3 + e4 + e5 + e6
assembly.Set(edges=tempSet, name='BCs-2')

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