# Function to create new surfaces in the assembly object and append them to the end of a list keeping track of all surfaces
def createSurface(assembly, surfaceName, objectName, catchPoint):
    assembly.Surface(name=surfaceName, side2Faces=assembly.instances[objectName].faces.findAt((catchPoint,)))

def createEdge(assembly, edgeName, objectName, catchPoint):
    assembly.Set(edges=assembly.instances[objectName].edges.findAt((catchPoint,)), name=edgeName)

model.Tie(
    adjust=ON,
    main=assembly.surfaces['surf-' + str(i)],
    name='Constraint' + str(i),
    positionToleranceMethod=COMPUTED,
    secondary=assembly.sets['edge-' + str(i)],
    thickness=ON,
    tieRotations=ON)

surfPartList = [
    # Plate
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
    'longFlange-2']

edgePartList = [
    # transStiff Bottom
    'transStiff-1',
    'transStiff-1',

    # transStiff Top 
    'transStiff-1',
    'transStiff-1',

    # longStiff Bottom
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',

    # longStiff Top
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2',
    'longStiff-2']