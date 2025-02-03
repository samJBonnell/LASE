# This program is the same as rev02 but (does not) use linear instance patterning to create the assembly instead of defining the geometry 
# within the sketch itself. Also allows easier indexing of internal sets for boundary constraints.

# Program Information
# This program is used as a baseline for defining an entire stiffened panel structure and is NOT parameterized to allow for
# iteration Once completed, this program will be used as a baseline to allow for the parameterization of the panel to allow 
# for optimization of the structure.

# Sam Bonnell - UBC LASE MASC Student
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
# - Define the geometry without constraints
#       - Internally defined sets
#       - Section assignments
# - Add constraints between the internal geometry
# - Add BCs and loads
# - Run the simulation
# - Add a log of all locations that intersect and collect them into a set
#       - Instance level as the boolean operations will create new lines from single entities

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
assembly.Surface(name='surf-plate', side2Faces=assembly.instances['plate-1'].faces.findAt(((0, 0, 0),)))

# transStiff
#   Two (2) x locations: 
#   (0, 0.25, 1.5), (0, 0.25, -1.5)
assembly.Surface(name='surf-transStiff-1', side2Faces=assembly.instances['transStiff-1'].faces.findAt(((0, 0.25, 1.5),)))
assembly.Surface(name='surf-transStiff-2', side2Faces=assembly.instances['transStiff-1'].faces.findAt(((0, 0.25, -1.5),)))

# transFlange
#   Two (2) x locations:
#   (0, 0.9, 1.5), (0, 0.9, -1.5)
assembly.Surface(name='surf-transFlange-1', side2Faces=assembly.instances['transFlange-1'].faces.findAt(((0, 0.9, 1.5),)))
assembly.Surface(name='surf-transFlange-2', side2Faces=assembly.instances['transFlange-1'].faces.findAt(((0, 0.9, -1.5),)))

# longStiff
#   Nine (9) x locations: 
#   (0, 0.25, 0),       (0.75, 0.25, 0),        (-0.75, 0.25, 0),
#   (0, 0.25, 1.75),    (0.75, 0.25, 1.75),     (-0.75, 0.25, 1.75),
#   (0, 0.25, -1.75),   (0.75, 0.25, -1.75),    (-0.75, 0.25, -1.75)
assembly.Surface(name='surf-longStiff-1', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((0, 0.25, 0),)))
assembly.Surface(name='surf-longStiff-2', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((0, 0.25, 1.75),)))
assembly.Surface(name='surf-longStiff-3', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((0, 0.25, -1.75),)))

assembly.Surface(name='surf-longStiff-4', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((0.75, 0.25, 0),)))
assembly.Surface(name='surf-longStiff-5', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((0.75, 0.25, 1.75),)))
assembly.Surface(name='surf-longStiff-6', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((0.75, 0.25, -1.75),)))

assembly.Surface(name='surf-longStiff-7', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((-0.75, 0.25, 0),)))
assembly.Surface(name='surf-longStiff-8', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((-0.75, 0.25, 1.75),)))
assembly.Surface(name='surf-longStiff-9', side2Faces=assembly.instances['longStiff-2'].faces.findAt(((-0.75, 0.25, -1.75),)))

# longFlange
#   Nine (9) x locations:
#   (0, 0.5, 0),        (0.75, 0.5, 0),       (-0.75, 0.5, 0),
#   (0, 0.5, 1.75),     (0.75, 0.5, 1.75),    (-0.75, 0.5, 1.75),
#   (0, 0.5, -1.75),    (0.75, 0.5, -1.75),   (-0.75, 0.5, -1.75)
assembly.Surface(name='surf-longFlange-1', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((0, 0.5, 0),)))
assembly.Surface(name='surf-longFlange-2', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((0, 0.5, 1.75),)))
assembly.Surface(name='surf-longFlange-3', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((0, 0.5, -1.75),)))

assembly.Surface(name='surf-longFlange-4', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((0.75, 0.5, 0),)))
assembly.Surface(name='surf-longFlange-5', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((0.75, 0.5, 1.75),)))
assembly.Surface(name='surf-longFlange-6', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((0.75, 0.5, -1.75),)))

assembly.Surface(name='surf-longFlange-7', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((-0.75, 0.5, 0),)))
assembly.Surface(name='surf-longFlange-8', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((-0.75, 0.5, 1.75),)))
assembly.Surface(name='surf-longFlange-9', side2Faces=assembly.instances['longFlange-2'].faces.findAt(((-0.75, 0.5, -1.75),)))

# Contact Points
# Vertical Constraints
# Transverse Stiffeners
#   Two (2) x locations: 
#   (0, 0, 1.5), (0, 0, -1.5)
e1 = assembly.instances['transStiff-1'].edges.findAt(((0,0.0,1.5),))
e2 = assembly.instances['transStiff-1'].edges.findAt(((0,0.0,-1.5),))
tempEdges = e1 + e2
assembly.Set(edges=tempEdges, name='edges-transStiff')

# Transverse Flanges
#   Two (2) x locations:
#   (0, 0.9, 1.5), (0, 0.9, -1.5)
e1 = assembly.instances['transStiff-1'].edges.findAt(((0, 0.9, 1.5),))
e2 = assembly.instances['transStiff-1'].edges.findAt(((0, 0.9, -1.5),))
tempEdges = e1 + e2
assembly.Set(edges=tempEdges, name='edges-transStiff2')

# Longitudinal Stiffeners
#   Nine (9) x locations: 
#   (0, 0, 0),          (0.75, 0, 0),       (-0.75, 0, 0),
#   (0, 0, 1.75),       (0.75, 0, 1.75),    (-0.75, 0, 1.75),
#   (0, 0, -1.75),      (0.75, 0, -1.75),   (-0.75, 0, -1.75)
e1 = assembly.instances['longStiff-2'].edges.findAt(((0.0, 0.0, 0.00),))
e2 = assembly.instances['longStiff-2'].edges.findAt(((0.0, 0.0, 1.75),))
e3 = assembly.instances['longStiff-2'].edges.findAt(((0.0, 0.0, -1.75),))
e4 = assembly.instances['longStiff-2'].edges.findAt(((0.75, 0.0, 0.00),))
e5 = assembly.instances['longStiff-2'].edges.findAt(((0.75, 0.0, 1.75),))
e6 = assembly.instances['longStiff-2'].edges.findAt(((0.75, 0.0, -1.75),))
e7 = assembly.instances['longStiff-2'].edges.findAt(((-0.75, 0.0, 0.0),))
e8 = assembly.instances['longStiff-2'].edges.findAt(((-0.75, 0.0, 1.75),))
e9 = assembly.instances['longStiff-2'].edges.findAt(((-0.75, 0.0, -1.75),))

tempEdges = e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9
assembly.Set(edges=tempEdges, name='edges-longStiff')

# Longitudinal Flanges
#   Nine (9) x locations:
#   (0, 0.5, 0),        (0.75, 0.5, 0),       (-0.75, 0.5, 0),
#   (0, 0.5, 1.75),     (0.75, 0.5, 1.75),    (-0.75, 0.5, 1.75),
#   (0, 0.5, -1.75),    (0.75, 0.5, -1.75),   (-0.75, 0.5, -1.75)
e1 = assembly.instances['longStiff-2'].edges.findAt(((0.0, 0.5, 0.00),))
e2 = assembly.instances['longStiff-2'].edges.findAt(((0.0, 0.5, 1.75),))
e3 = assembly.instances['longStiff-2'].edges.findAt(((0.0, 0.5, -1.75),))
e4 = assembly.instances['longStiff-2'].edges.findAt(((0.75, 0.5, 0.00),))
e5 = assembly.instances['longStiff-2'].edges.findAt(((0.75, 0.5, 1.75),))
e6 = assembly.instances['longStiff-2'].edges.findAt(((0.75, 0.5, -1.75),))
e7 = assembly.instances['longStiff-2'].edges.findAt(((-0.75, 0.5, 0.0),))
e8 = assembly.instances['longStiff-2'].edges.findAt(((-0.75, 0.5, 1.75),))
e9 = assembly.instances['longStiff-2'].edges.findAt(((-0.75, 0.5, -1.75),))

tempEdges = e1 + e2 + e3 + e4 + e5 + e6 + e7 + e8 + e9
assembly.Set(edges=tempEdges, name='edges-longStiff2')

# ----------------------------------------------------------------------------------------------------------------------------------

# Create TIE constraints from all of the above created sets!
# Plate -> Transverse Stiffeners
model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-plate'],
    name='Constraint-1',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-transStiff'],
    thickness=ON,
    tieRotations=ON)

# Transverse Stiffeners -> Transverse Flanges
model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-transFlange-1'],
    name='Constraint-2',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-transStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-transFlange-2'],
    name='Constraint-3',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-transStiff2'],
    thickness=ON,
    tieRotations=ON)

# Plate -> Longitudinal Stiffeners
model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-plate'],
    name='Constraint-4',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff'],
    thickness=ON,
    tieRotations=ON)

# Longitudinal Stiffeners -> Longitudinal Flanges
model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-1'],
    name='Constraint-5',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-2'],
    name='Constraint-6',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-3'],
    name='Constraint-7',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-4'],
    name='Constraint-8',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-5'],
    name='Constraint-9',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-6'],
    name='Constraint-10',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-7'],
    name='Constraint-11',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-8'],
    name='Constraint-12',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-longFlange-9'],
    name='Constraint-13',
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edges-longStiff2'],
    thickness=ON,
    tieRotations=ON)

# Create Step Object
model.StaticStep(name='Step-1', previous='Initial')