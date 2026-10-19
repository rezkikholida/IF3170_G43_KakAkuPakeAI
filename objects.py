import random
import string
from visualization import visualize

#
#  CLASS DEFINITIONS
#

class dimensions():     # Represents the dimension attribute
    def __init__(self, width, length, height):
        self.width = width
        self.length = length
        self.height = height

    def __repr__(self):
        return f"(w = {self.width}, l = {self.length}, h = {self.height})"    
    

class orientation():    # Represents the orientation attribute and how packages are oriented/manipulated
    def __init__(self):

        self.Xaxis = "w"
        self.Yaxis = "l"
        self.Zaxis = "h"

        self.coordinates = []
        self.inside = True

    def __repr__(self):
        return f"(X: {self.Xaxis}, Y: {self.Yaxis}, Z: {self.Zaxis}, Coordinates = {self.coordinates}, Inside Truck: {self.inside})"


class package(object):  # Represents the package object as a whole
    def __init__(self, id, Dimensions, Orientation, Value, Weight, IsFragile, Eta):
        self.id = id
        self.Dimensions = Dimensions
        self.Orientation = Orientation
        self.Value = Value
        self.Weight = Weight
        self.IsFragile = IsFragile
        self.Eta = Eta

        self.alignedPackagesX = [self]
        self.alignedPackagesY = [self]
        self.alignedPackagesZ = [self]

        self.keepingArrayX = [self]
        self.keepingArrayY = [self]
        self.keepingArrayZ = [self]

        self.totalX = self.Dimensions.width
        self.totalY = self.Dimensions.length
        self.totalZ = self.Dimensions.height

        self.maxRangeX = 0
        self.maxRangeY = 0 
        self.maxRangeZ = 0 

    def __repr__(self):
        return f"\nPackage (ID = {self.id}, {self.Dimensions}, {self.Orientation},\nValue = {self.Value}, Weight = {self.Weight}, IsFragile = {self.IsFragile}, ETA (day) = {self.Eta})\n"

    # To be worked on
    def rotate(self, inquiry, listofObjects):      # Rotate in accordance to the inquiry
        if inquiry == "x":
            placeholder = self.Dimensions.height
            self.Dimensions.height = self.Dimensions.length
            self.Dimensions.length = placeholder

        elif inquiry == "y":
            placeholder = self.Dimensions.length
            self.Dimensions.length = self.Dimensions.width
            self.Dimensions.width = placeholder

        elif inquiry == "z":
            placeholder = self.Dimensions.height
            self.Dimensions.height = self.Dimensions.width
            self.Dimensions.width = placeholder

        self.retrace(listofObjects)

    def trade(self, targetObject, listofObjects):       # Trade objects and their locations
        placeholderX = self.Dimensions.width
        placeholderY = self.Dimensions.length
        placeholderZ = self.Dimensions.height
        placeholderCoordinatesX = self.Orientation.coordinates[0]
        placeholderCoordinatesY = self.Orientation.coordinates[2]
        placeholderCoordinatesZ = self.Orientation.coordinates[1]

        self.Dimensions.width = targetObject.Dimensions.width
        self.Dimensions.length = targetObject.Dimensions.length
        self.Dimensions.height = targetObject.Dimensions.height
        self.Orientation.coordinates[0] = targetObject.Orientation.coordinates[0]
        self.Orientation.coordinates[2] = targetObject.Orientation.coordinates[2]
        self.Orientation.coordinates[1] = targetObject.Orientation.coordinates[1]

        targetObject.Dimensions.width = placeholderX
        targetObject.Dimensions.length = placeholderY
        targetObject.Dimensions.height = placeholderZ
        targetObject.Orientation.coordinates[0] = placeholderCoordinatesX
        targetObject.Orientation.coordinates[2] = placeholderCoordinatesY
        targetObject.Orientation.coordinates[1] = placeholderCoordinatesZ

        self.retrace(listofObjects)

    def relocate(self, setofCoordinates, listofObjects):
        self.Orientation.coordinates[0] = setofCoordinates[0]
        self.Orientation.coordinates[2] = setofCoordinates[2]
        self.Orientation.coordinates[1] = setofCoordinates[1]

        checkPlacement = ""

        if setofCoordinates[2] >= 0:
            checkPlacement = "vertical"

        if isOccupied(listofObjects, self, setofCoordinates, checkPlacement)[0] == True: 
            return 0

        self.retrace(listofObjects)

    def retrace(self, listofObjects, truckObj=None):  # Helps adjust for the changes done by trading, relocating, or rotating

        self.maxRangeX = self.Orientation.coordinates[0] + self.Dimensions.width
        self.maxRangeY = self.Orientation.coordinates[1] + self.Dimensions.length
        self.maxRangeZ = self.Orientation.coordinates[2] + self.Dimensions.height

        self.totalX = self.Dimensions.width
        self.totalY = self.Dimensions.length
        self.totalZ = self.Dimensions.height

        i = 0
        j = 0

        while i < len(listofObjects):      # Rework objects' relation to each other and their coordinates
            if self.id == listofObjects[i].id:
                i += 1
                continue

            if self.Orientation.coordinates[0] <= listofObjects[i].Orientation.coordinates[0] <= self.maxRangeX:
                if listofObjects[i] not in self.keepingArrayX:
                    self.keepingArrayX.append(listofObjects[i])
                if self not in listofObjects[i].keepingArrayX:
                    listofObjects[i].keepingArrayX.append(self)

                self.totalX += listofObjects[i].Dimensions.width
                listofObjects[i].totalX += self.Dimensions.width

            # USE OBJECT COORDINATES TO MAKE SURE IT ONLY APPLIES TO OBJECTS STACKED ON EACH OTHER
            # CHECK IF THE CODE REFLECTS THE RELATIONS BETWEEN 2 OBJECTS OR IF IT'S ONLY BETWEEN ITSELF VVV
            if listofObjects[i].Orientation.coordinates[2] > 0:
                if self.Orientation.coordinates[2] <= listofObjects[i].Orientation.coordinates[2] <= self.maxRangeZ:
                    if listofObjects[i] not in self.keepingArrayY:
                        self.keepingArrayY.append(listofObjects[i])
                    if self not in listofObjects[i].keepingArrayZ:
                        listofObjects[i].keepingArrayZ.append(self)

                    self.totalZ += listofObjects[i].Dimensions.height
                    listofObjects[i].totalZ += self.Dimensions.height

            if self.Orientation.coordinates[1] <= listofObjects[i].Orientation.coordinates[1] <= self.maxRangeY:
                if listofObjects[i] not in self.keepingArrayY:
                    self.keepingArrayY.append(listofObjects[i])
                if self not in listofObjects[i].keepingArrayY:
                    listofObjects[i].keepingArrayY.append(self)

                self.totalY += listofObjects[i].Dimensions.length
                listofObjects[i].totalY += self.Dimensions.length

            i += 1

        # After processing all objects, update inside status for every object
        if truckObj is None:
            truckObj = truck()
        while j < len(listofObjects):
            if len(listofObjects[j].Orientation.coordinates) < 3:
                j += 1
                continue

            # Red (inside == False) when the placed box violates the truck's width, length, or height
            updateInside(listofObjects[j], truckObj.Dimensions.width, truckObj.Dimensions.length, truckObj.Dimensions.height)

            listofObjects[j].alignedPackagesX = listofObjects[j].keepingArrayX[:]
            listofObjects[j].alignedPackagesY = listofObjects[j].keepingArrayY[:]
            listofObjects[j].alignedPackagesZ = listofObjects[j].keepingArrayZ[:]

            j += 1
        

class truck(object):    # Represents the truck object as a whole
    def __init__(self):
        self.Dimensions = dimensions(10, 20, 5)
        self.MaxCapacity = 500

    def __repr__(self):
            return f"Truck({self.Dimensions}, Capacity = {self.MaxCapacity})"

#
#  FUNCTION DEFINITIONS
#

def fitting():  # Helps with initializing the placements of the packages within the truck
    placement = ["horizontal", "vertical", "spatial"]

    return random.choice(placement)


# Positioning functions
def xStatus(listofObjects, currentObject, count):

    if listofObjects[count].Orientation.coordinates[0] <= currentObject.maxRangeX <= listofObjects[count].maxRangeX and currentObject.Orientation.coordinates[1] <= listofObjects[count].maxRangeY <= currentObject.maxRangeY:
        return True
    
    return False


def yStatus(listofObjects, currentObject, count):

    if listofObjects[count].Orientation.coordinates[1] <= currentObject.maxRangeY <= listofObjects[count].maxRangeY and currentObject.Orientation.coordinates[0] <= listofObjects[count].maxRangeX <= currentObject.maxRangeX:
        return True
    
    return False


def zStatus(listofObjects, currentObject, count, xStat, yStat):
    xStat = xStatus(listofObjects, currentObject, count)
    yStat = yStatus(listofObjects, currentObject, count)

    if xStat == True or yStat == True:
        if listofObjects[count].Orientation.coordinates[2] <= currentObject.maxRangeZ <= listofObjects[count].maxRangeZ or currentObject.maxRangeZ > listofObjects[count].maxRangeZ:
            return True

        return False
    
    return False


def isOccupied(listofObjects, currentObject=None, coordinates=None, fitting="horizontal", startIndex=None, limit=None):  # Checks whether a position overlaps with any other object
    coords = coordinates if coordinates is not None else (currentObject.Orientation.coordinates if currentObject is not None else None)
    if coords is None or len(coords) < 3:
        return False, None

    x1, y1, z1 = coords[0], coords[1], coords[2]
    w1 = currentObject.Dimensions.width if currentObject is not None else 0
    l1 = currentObject.Dimensions.length if currentObject is not None else 0
    h1 = currentObject.Dimensions.height if currentObject is not None else 0

    end = limit if limit is not None else len(listofObjects)
    start = startIndex if startIndex is not None else 0
    for obj in listofObjects[start:end]:
        if currentObject is not None and obj.id == currentObject.id:
            continue
        if len(obj.Orientation.coordinates) < 3:
            continue

        x2, y2, z2 = obj.Orientation.coordinates[0], obj.Orientation.coordinates[1], obj.Orientation.coordinates[2]
        w2, l2, h2 = obj.Dimensions.width, obj.Dimensions.length, obj.Dimensions.height

        overlapX = min(x1 + w1, x2 + w2) - max(x1, x2)
        overlapY = min(y1 + l1, y2 + l2) - max(y1, y2)
        overlapZ = min(z1 + h1, z2 + h2) - max(z1, z2)

        if overlapX > 0 and overlapY > 0 and overlapZ > 0:
            return True, obj.Dimensions

    return False, None    


def updateInside(currentObject, maxWidth, maxLength, maxHeight):
    # A package is "inside" only when its whole placed box stays within the truck.
    # If its coordinates push it past the truck's width, length, or height, it is a
    # violation and gets marked so the visualization colors it red.
    coordinates = currentObject.Orientation.coordinates

    if len(coordinates) < 3:
        return

    currentObject.Orientation.inside = (
        coordinates[0] >= 0 and currentObject.Dimensions.width <= maxWidth and
        currentObject.Orientation.coordinates[0] + currentObject.Dimensions.width <= maxWidth and
        coordinates[1] >= 0 and currentObject.Orientation.coordinates[1] + currentObject.Dimensions.length <= maxLength and
        coordinates[2] >= 0 and currentObject.Orientation.coordinates[2] + currentObject.Dimensions.height <= maxHeight
    )


def pushAbove(listofObjects, currentObject):    # Guaranteed non-overlapping fallback: stack above everything it shares a footprint with
    coordinates = currentObject.Orientation.coordinates
    top = coordinates[2]

    for obj in listofObjects:
        if obj.id == currentObject.id or len(obj.Orientation.coordinates) < 3:
            continue

        other = obj.Orientation.coordinates
        overlapX = min(coordinates[0] + currentObject.Dimensions.width, other[0] + obj.Dimensions.width) - max(coordinates[0], other[0])
        overlapY = min(coordinates[1] + currentObject.Dimensions.length, other[1] + obj.Dimensions.length) - max(coordinates[1], other[1])

        if overlapX > 0 and overlapY > 0:
            top = max(top, other[2] + obj.Dimensions.height)

    currentObject.Orientation.coordinates[2] = top
    currentObject.maxRangeX = currentObject.Orientation.coordinates[0] + currentObject.Dimensions.width
    currentObject.maxRangeY = currentObject.Orientation.coordinates[1] + currentObject.Dimensions.length
    currentObject.maxRangeZ = currentObject.Orientation.coordinates[2] + currentObject.Dimensions.height


def make_package():     # Creates a package
    rng = random.randint(3,4)
    
    pack_id = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=rng-1)) + "Package"
    pack_dim = dimensions((random.randint(1,10)), (random.randint(1,20)), (random.randint(1,5)))
    pack_orient = orientation()
    pack_value = random.randint(0,100)
    pack_weight = random.randint(0,100)
    pack_isFragile = bool(random.getrandbits(1))
    pack_Eta = random.randint(0,5)

    Package = package(pack_id, pack_dim, pack_orient, pack_value, pack_weight, pack_isFragile, pack_Eta)
    return Package


def nonVerticalAppendation(listofObjects, checkPlacement, maxWidth, maxLength, maxHeight, i):
    j = 0
    current = listofObjects[i]

    x_coor = random.randint(0, max(0, maxWidth - current.Dimensions.width))
    y_coor = random.randint(0, max(0, maxLength - current.Dimensions.length))
    z_coor = 0

    # Try to find a non-overlapping floor position so packages never merge
    attempts = 0
    maxAttempts = 25
    while isOccupied(listofObjects, current, [x_coor, y_coor, z_coor], checkPlacement, startIndex=0, limit=i)[0] and attempts < maxAttempts:
        x_coor = random.randint(0, max(0, maxWidth - current.Dimensions.width))
        y_coor = random.randint(0, max(0, maxLength - current.Dimensions.length))
        z_coor = 0
        attempts += 1

    # A coordinate will get appended according to MaxRange 
    current.Orientation.coordinates.clear()
    current.Orientation.coordinates.append(x_coor)
    current.Orientation.coordinates.append(y_coor)
    current.Orientation.coordinates.append(z_coor)

    current.maxRangeX = current.Orientation.coordinates[0] + current.Dimensions.width
    current.maxRangeY = current.Orientation.coordinates[1] + current.Dimensions.length
    current.maxRangeZ = current.Orientation.coordinates[2] + current.Dimensions.height

    # If the floor is too packed, lift the package above every box it would merge into
    if isOccupied(listofObjects, current, current.Orientation.coordinates, checkPlacement)[0]:
        pushAbove(listofObjects, current)

    # Red (inside == False) when the placed box violates the truck's width, length, or height
    updateInside(current, maxWidth, maxLength, maxHeight)

    if i >= 1:
        while j < i:
            if listofObjects[j].Orientation.coordinates[0] <= current.Orientation.coordinates[0] <= listofObjects[j].maxRangeX:
                listofObjects[j].alignedPackagesX.append(current)
                current.alignedPackagesX.append(listofObjects[j])

                listofObjects[j].totalX += current.Dimensions.width
                current.totalX += listofObjects[j].Dimensions.width

            if listofObjects[j].Orientation.coordinates[1] <= current.Orientation.coordinates[1] <= listofObjects[j].maxRangeY:
                listofObjects[j].alignedPackagesY.append(current)
                current.alignedPackagesY.append(listofObjects[j])

                listofObjects[j].totalY += current.Dimensions.length
                current.totalY += listofObjects[j].Dimensions.length

            j += 1


def initialize():    # Initialize a truck object and random amounts of packages 
    rng = 3 #random.randint(1,10)
    i = 0
    
    myTruck = truck()
    pack_objects = []

    maxWidth = myTruck.Dimensions.width      # Defines the upper limit of the boundaries to stay inside the truck
    maxLength = myTruck.Dimensions.length
    maxHeight = myTruck.Dimensions.height

    while i <= rng:   # Creates the objects and the orientations
        pack_objects.append(make_package())

        checkPlacement = fitting()        

        if checkPlacement == "vertical" and i >= 1:
            current = pack_objects[i]

            # Only already-placed, non-fragile packages (they have coordinates) can act as a base
            candidates = [
                obj for obj in pack_objects[:i]
                if len(obj.Orientation.coordinates) >= 3 and obj.IsFragile == False
            ]

            placedVertically = False
            tries = 0

            while candidates and tries < 5 and not placedVertically:
                selectedBottom = random.choice(candidates)

                x_coor = selectedBottom.Orientation.coordinates[0]
                y_coor = selectedBottom.Orientation.coordinates[1]
                z_coor = selectedBottom.Orientation.coordinates[2] + selectedBottom.Dimensions.height

                if not isOccupied(pack_objects, current, [x_coor, y_coor, z_coor], checkPlacement)[0]:
                    current.alignedPackagesY.append(selectedBottom)

                    current.Orientation.coordinates.clear()
                    current.Orientation.coordinates.append(x_coor)
                    current.Orientation.coordinates.append(y_coor)
                    current.Orientation.coordinates.append(z_coor)

                    current.maxRangeX = current.Orientation.coordinates[0] + current.Dimensions.width
                    current.maxRangeY = current.Orientation.coordinates[1] + current.Dimensions.length
                    current.maxRangeZ = current.Orientation.coordinates[2] + current.Dimensions.height

                    placedVertically = True

                tries += 1

            if not placedVertically:
                checkPlacement = random.choice(["horizontal", "spatial"])
                nonVerticalAppendation(pack_objects, checkPlacement, maxWidth, maxLength, maxHeight, i)
            
        else:
            nonVerticalAppendation(pack_objects, checkPlacement, maxWidth, maxLength, maxHeight, i)

        updateInside(pack_objects[i], maxWidth, maxLength, maxHeight)

        i += 1

    print(pack_objects,"\n")
    print(myTruck)
    print("\n")

#    print(pack_objects[0].maxRangeX, pack_objects[0].maxRangeY, pack_objects[0].maxRangeZ, "\n")
#    print(pack_objects[0].totalX, pack_objects[0].totalY, pack_objects[0].totalZ)

    return pack_objects, myTruck

def testing():
    t = initialize()
    visualize(t[0])

testing()

# WIP
# PLEASE MAKE SURE THIS IS CONSISTENT
# X = WIDTH, Y = HEIGHT, Z = LENGTH