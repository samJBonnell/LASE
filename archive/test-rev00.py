# Parameters defining the geometry of the plate
# Can be loaded into the program via outside programs...
# Quote: this can be used for optimization!

# # Plate Dimensions
# plate_width = 3
# plate_length = 6
# plate_thickness = 0.010

# # Transverse Stiffener Dimensions
# transverse_height = 0.15
# transverse_thickness = 0.010
# transverse_num = 2

# # Longitudinal Stiffener Dimensions
# longitudinal_height = 0.10
# longitudinal_thickness = 0.010
# longitudinal_num = 5

# # Transverse Flange Dimensions
# transverseFlange_width = 0.150
# transverseFlange_thickness = 0.010

# # Longitudinal Flange Dimensions
# longitudinalFlange_width = 0.20
# longitudinalFlange_thickness = 0.010

# Task List
# 1. Extrude a non-square unit to observe how dimensions are handled from the 2D sketches
#       - Sketches are defined in the x-y plane and extruded in the z-axis
# 2. Create transverse stiffeners & attach them
#       - Potentially through the use of instancing
#       - Need to create internal sets first and use them to define contact geometry
# 3. Create longitudinal flanges & attach them
# 4. Create transverse flanges & attach them
# 5. Define BCs
# 6. Add loading and run simulation
# 7. Parametrize the model


# ABAQUS Python Section

from abaqus import *
from abaqusConstants import *
backwardCompatibility.setValues(includeDeprecated=True, reportDeprecated=False)

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

session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

# del model
# Create model, assembly, & viewport
model = mdb.Model(name="model")
# assembly = model.rootAssembly(name="assembly")
# viewport = session.Viewport(name="viewport",origin=(0,0), width=150, height=120)

# Plate part
model.Part(
    name='plate',
    dimensionality=THREE_D, 
    type=DEFORMABLE_BODY)

# Transverse Stiffener Part
model.Part(
    name='transStiffener',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

# Transverse Flange Part
model.Part(
    name='transFlange',
    dimensionality=THREE_D,
    type=DEFORMABLE_BODY)

# # Longitudinal Stiffener Part
# model.Part(
#     name='longStiffener',
#     dimensionality=THREE_D,
#     type=DEFORMABLE_BODY)

# # Longitudinal Flange Part
# model.Part(
#     name='longFlange',
#     dimensionality=THREE_D,
#     type=DEFORMABLE_BODY)

# Plate sketch and part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(-1.5, 0.0), point2=(1.5, 0.0))
model.sketches['profileSketch'].HorizontalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)

model.parts['plate'].BaseShellExtrude(depth=6.0, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# Transverse Stiffener sketch and part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(0.0, 0.0), point2=(0.0, 0.9))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(1.5, 0.0), point2=(1.5, 0.9))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[3], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(-1.5, 0.0), point2=(-1.5, 0.9))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[4], addUndoState=False)

model.parts['transStiffener'].BaseShellExtrude(depth=6.0, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# Longitudinal Stiffener sketch and part
model.ConstrainedSketch(name='profileSketch', sheetSize=200.0)
model.sketches['profileSketch'].Line(point1=(0.0, 0.0), point2=(0.0, 0.5))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[2], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(1.5, 0.0), point2=(1.5, 0.5))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[3], addUndoState=False)
model.sketches['profileSketch'].Line(point1=(3, 0.0), point2=(3, 0.5))
model.sketches['profileSketch'].VerticalConstraint(entity=model.sketches['profileSketch'].geometry[4], addUndoState=False)

model.parts['transFlange'].BaseShellExtrude(depth=1.5, sketch=model.sketches['profileSketch'])
del model.sketches['profileSketch']

# Create Material Defintions
model.Material(name='steel')
model.materials['steel'].Elastic(table=((200000000000.0,0.3),))

# Section Defintions
model.HomogeneousShellSection(
    idealization=NO_IDEALIZATION,
    integrationRule=SIMPSON,
    material='steel',
    name='t_plate',
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

# Collect faces and create a set from target faces
model.parts['plate'].Set(faces=model.parts['plate'].faces.findAt(((0,0,1.5),)) , name='Set-plate')

v1 = model.parts['transStiffener'].faces.findAt(((0,0.45,1.5),))
v2 = model.parts['transStiffener'].faces.findAt(((-1.5,0.45,1.5),))
v3 = model.parts['transStiffener'].faces.findAt(((1.5,0.45,1.5),))
stiffFaces = v1 + v2 + v3
model.parts['transStiffener'].Set(faces=stiffFaces, name='Set-transStiff')

v1 = model.parts['transFlange'].faces.findAt(((0,0.25,0.75),))
v2 = model.parts['transFlange'].faces.findAt(((1.5,0.25,0.75),))
v3 = model.parts['transFlange'].faces.findAt(((3.0,0.25,0.75),))
stiffFaces = v1 + v2 + v3
model.parts['transFlange'].Set(faces=stiffFaces, name='Set-transFlange')

# Assign section properties to each of the parts
model.parts['plate'].SectionAssignment(
    offset=0.0, 
    offsetField='', 
    offsetType=MIDDLE_SURFACE, 
    region=model.parts['plate'].sets['Set-plate'],
    sectionName='t_plate',
    thicknessAssignment=FROM_SECTION)

model.parts['transStiffener'].SectionAssignment(
    offset=0.0, 
    offsetField='', 
    offsetType=MIDDLE_SURFACE, 
    region=model.parts['transStiffener'].sets['Set-transStiff'],
    sectionName='t_plate',
    thicknessAssignment=FROM_SECTION)

model.parts['transFlange'].SectionAssignment(
    offset=0.0, 
    offsetField='', 
    offsetType=MIDDLE_SURFACE, 
    region=model.parts['transFlange'].sets['Set-transFlange'],
    sectionName='t_plate',
    thicknessAssignment=FROM_SECTION)

# Create the assembly and instance individual parts
model.rootAssembly.DatumCsysByDefault(CARTESIAN)
model.rootAssembly.Instance(dependent=ON, name='plate-1', part=model.parts['plate'])
model.rootAssembly.Instance(dependent=ON, name='transStiff-1', part=model.parts['transStiffener'])
model.rootAssembly.Instance(dependent=ON, name='transFlange-1', part=model.parts['transFlange'])
model.rootAssembly.rotate(instanceList=['transFlange-1'], axisPoint=(0.0,0.0,0.0), axisDirection=(0.0,1.0,0.0), angle=90)

# Create a step in the simulation
model.StaticStep(name='Step-1', previous='Initial')

# Boundary conditions and contacts
model.rootAssembly.Surface(name='m_Surf-1',side2Faces=model.rootAssembly.instances['plate-1'].faces.findAt(((0,0,1.5),)))

v1 = model.rootAssembly.instances['transStiff-1'].edges.findAt(((0.0,0.0,1.5),))
v2 = model.rootAssembly.instances['transStiff-1'].edges.findAt(((-1.5,0.0,1.5),))
v3 = model.rootAssembly.instances['transStiff-1'].edges.findAt(((1.5,0.0,1.5),))
stiffEdges = v1 + v2 + v3
model.rootAssembly.Set(edges=stiffEdges , name='s_Set-1')

# Create tie boundary constraint on plate and web/flange
model.Tie(
    adjust=ON,
    main=model.rootAssembly.surfaces['m_Surf-1'],
    name='Constraint-1',
    positionToleranceMethod=COMPUTED,
    secondary=model.rootAssembly.sets['s_Set-1'],
    thickness=ON,
    tieRotations=ON)