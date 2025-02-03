# This program is the same as rev03 but uses for loops and some higher better file management to handle the large number of constraints

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

# ----------------------------------------------------------------------------------------------------------------------------------

def createSurface(assembly, surfaceName, objectName, catchPoint):
    assembly.Surface(name=surfaceName, side2Faces=assembly.instances[objectName].faces.findAt((catchPoint,)))

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

def createEdge(assembly, edgeName, objectName, catchPoint):
    assembly.Set(edges=assembly.instances[objectName].edges.findAt((catchPoint,)), name=edgeName)

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

# Section Assignment
assignSection(model, 'plate', 'plate-0010', [(0,0,0)])
assignSection(model, 'transStiff', 'plate-0010', [(-1.5, 0.45, 1.5), (1.5, 0.45, 1.5)])
assignSection(model, 'transFlange', 'plate-0010', [(-1.5, 0.9, 1.5), (1.5, 0.9, 1.5)])
assignSection(model, 'longStiff', 'plate-0010', [(0, 0.25, 1.5), (0.75, 0.25, 1.5), (-0.75, 0.25, 1.5)])
assignSection(model, 'longFlange', 'plate-0010', [(0, 0.5, 1.5), (0.75, 0.5, 1.5), (-0.75, 0.5, 1.5)])

# Assembly & Instances
model.rootAssembly.DatumCsysByDefault(CARTESIAN)
assembly = model.rootAssembly

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

# ----------------------------------------------------------------------------------------------------------------------------------

# Contact Surfaces
# Planes that define contact pairs within the part
# Set Names:
# plate
#   One (1) x locations:
#   (0, 0, 0)
# assembly.Surface(name='surf-plate', side2Faces=assembly.instances['plate-1'].faces.findAt(((0, 0, 0),)))

surfPartList = [
    'plate-1',

    'transStiff-1',
    'transStiff-1',

    'transFlange-1',
    'transFlange-1',

    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',]

edgePartList = [
    'transStiff-1',
    'transStiff-1',

    'transStiff-1',
    'transStiff-1',

    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',

    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',
    'longFlange-2',]

surfPoints = [
    # plate
    (0, 0, 0),

    # transStiff
    (0, 0.25, 1.5),
    (0, 0.25, -1.5),

    # transFlange
    (0, 0.9, 1.5),
    (0, 0.9, -1.5),

    # longFlange
    (0, 0.5, 0),
    (0, 0.5, 1.75),
    (0, 0.5, -1.75),
    (0.75, 0.5, 0),
    (0.75, 0.5, 1.75),
    (0.75, 0.5, -1.75),
    (-0.75, 0.5, 0),
    (-0.75, 0.5, 1.75),
    (-0.75, 0.5, -1.75),
    
    (0, 0.25, 0),
    (0, 0.25, 1.75),
    (0, 0.25, -1.75),
    (0.75, 0.25, 0),
    (0.75, 0.25, 1.75),
    (0.75, 0.25, -1.75),
    (-0.75, 0.25, 0),
    (-0.75, 0.25, 1.75),
    (-0.75, 0.25, -1.75)]

edgePoints = [
    # Vertical Constraints
    # transStiff Bottom
    (0,0.0,1.5),
    (0,0.0,-1.5),

    # transStiff Top
    (0, 0.9, 1.5),
    (0, 0.9, -1.5),

    # longStiff Bottom
    (0.0, 0.0, 0.0),
    (0.0, 0.0, 1.75),
    (0.0, 0.0, -1.75),
    (0.75, 0.0, 0.0),
    (0.75, 0.0, 1.75),
    (0.75, 0.0, -1.75),
    (-0.75, 0.0, 0.0),
    (-0.75, 0.0, 1.75),
    (-0.75, 0.0, -1.75),

    # longStiff Top
    (0.0, 0.5, 0.0),
    (0.0, 0.5, 1.75),
    (0.0, 0.5, -1.75),
    (0.75, 0.5, 0.0),
    (0.75, 0.5, 1.75),
    (0.75, 0.5, -1.75),
    (-0.75, 0.5, 0.0),
    (-0.75, 0.5, 1.75),
    (-0.75, 0.5, -1.75),
    
    # Horizontal Constraints
    # longStiff End
    (0, 0.25, 1.5),
    (0, 0.25, -1.5),
    (0.75, 0.25, 1.5),
    (0.75, 0.25, -1.5),
    (-0.75, 0.25, 1.5),
    (-0.75, 0.25, -1.5),

    (0, 0.5, 1.5),
    (0, 0.5, -1.5),
    (0.75, 0.5, 1.5),
    (0.75, 0.5, -1.5),
    (-0.75, 0.5, 1.5),
    (-0.75, 0.5, -1.5)
    ]

# Create TIE constraints from all of the above created sets!
constraintIndex = [
    # transStiff Bottom
    0,
    0,
    
    # transStiff Top
    3,
    4,

    # longStiff Bottom
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,

    # longStiff Top
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    
    # Horizontal Constraints
    1,
    2,
    1,
    2,
    1,
    2,
    
    1,
    2,
    1,
    2,
    1,
    2]

for i in range(len(surfPoints)):
    createSurface(assembly, 'surf-' + str(i), surfPartList[i], surfPoints[i])

for i in range(len(edgePoints)):
    createEdge(assembly, 'edge-' + str(i), edgePartList[i], edgePoints[i])

for i in range(len(constraintIndex)):
    model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-' + str(constraintIndex[i])],
    name='Constraint' + str(i),
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edge-' + str(i)],
    thickness=ON,
    tieRotations=ON)

# Boundary Conditions

# ----------------------------------------------------------------------------------------------------------------------------------

# Create Step Object
model.StaticStep(name='Step-1', previous='Initial')