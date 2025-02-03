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

# Create Step Object
model.StaticStep(name='Step-1', previous='Initial')