# hillclimbing_stepestaccent.py
import random
import time
from copy import deepcopy
from objects import (initialize, isOccupied, updateInside, fitting, truck)
from visualization import visualize


# Objects.py helper
def stateValue(ListofObjects):
    totalWeight = 0
    for obj in ListofObjects:
        if getattr(obj.Orientation, 'inside', False):
            totalWeight += obj.Weight
    return totalWeight


def candidateCoordinates(listofObjects, i):
    current = listofObjects[i]
    candidates = []

    maxWidth = 10
    maxLength = 20
    maxHeight = 5

    for x in range(maxWidth - current.Dimensions.width + 1):
        for y in range(maxLength - current.Dimensions.length + 1):
            z = 0
            coordinates = [x, y, z]

            if z + current.Dimensions.height <= maxHeight and not isOccupied(listofObjects, current, coordinates)[0]:
                candidates.append(coordinates)

    return candidates


def safe_rotate(obj, axis, listofObjects):
    original_dims = (obj.Dimensions.width, obj.Dimensions.length, obj.Dimensions.height)

    if axis == "x":
        obj.Dimensions.length, obj.Dimensions.height = obj.Dimensions.height, obj.Dimensions.length
    elif axis == "y":
        obj.Dimensions.width, obj.Dimensions.height = obj.Dimensions.height, obj.Dimensions.width
    elif axis == "z":
        obj.Dimensions.width, obj.Dimensions.length = obj.Dimensions.length, obj.Dimensions.width
    else:
        return False

    if isOccupied(listofObjects, obj, obj.Orientation.coordinates)[0]:
        obj.Dimensions.width, obj.Dimensions.length, obj.Dimensions.height = original_dims
        return False

    obj.retrace(listofObjects)
    return True


def safe_trade(obj1, obj2, listofObjects):
    if obj2 is None or obj2 is obj1:
        return False

    obj1.trade(obj2, listofObjects)
    return True


def safe_relocate(obj, setofCoordinates, listofObjects):
    if setofCoordinates is None or len(setofCoordinates) < 3:
        return False

    checkPlacement = "vertical" if setofCoordinates[2] >= 0 else "horizontal"

    if isOccupied(listofObjects, obj, setofCoordinates, checkPlacement)[0]:
        return False

    obj.relocate(setofCoordinates, listofObjects)
    return True


# Generate neighbors 
def rotateNeighbors(ListofObjects):
    neighbors = []
    values = []
    operations = []

    for i in range(len(ListofObjects)):
        for axis in ["x", "y", "z"]:
            neighbor = deepcopy(ListofObjects)

            success = safe_rotate(neighbor[i], axis, neighbor)

            if not success:
                continue

            neighbors.append(neighbor)
            values.append(stateValue(neighbor))
            operations.append({"type": "rotate", "package": neighbor[i].id, "axis": axis})

    return neighbors, values, operations


def tradeNeighbors(ListofObjects):
    neighbors = []
    values = []
    operations = []

    for i in range(len(ListofObjects)):
        for j in range(i + 1, len(ListofObjects)):
            neighbor = deepcopy(ListofObjects)

            success = safe_trade(neighbor[i], neighbor[j], neighbor)

            if not success:
                continue

            neighbors.append(neighbor)
            values.append(stateValue(neighbor))
            operations.append({"type": "trade", "package1": neighbor[i].id, "package2": neighbor[j].id})

    return neighbors, values, operations


def relocateNeighbors(ListofObjects, i):
    neighbors = []
    values = []
    operations = []

    coordinatesList = candidateCoordinates(ListofObjects, i)

    for coordinates in coordinatesList:
        neighbor = deepcopy(ListofObjects)
        old_coordinates = neighbor[i].Orientation.coordinates[:]

        success = safe_relocate(neighbor[i], coordinates, neighbor)

        if success:
            neighbors.append(neighbor)
            values.append(stateValue(neighbor))
            operations.append({"type": "relocate", "package": neighbor[i].id, "from": old_coordinates, "to": coordinates[:]})

    return neighbors, values, operations


def neighborList(listofObjects, i):
    neighborRotate, valuesRotate, opsRotate = rotateNeighbors(listofObjects)
    neighborTrade, valuesTrade, opsTrade = tradeNeighbors(listofObjects)
    neighborRelocate, valuesRelocate, opsRelocate = relocateNeighbors(listofObjects, i)

    valid_neighbor = neighborRotate + neighborTrade + neighborRelocate
    valid_values = valuesRotate + valuesTrade + valuesRelocate
    valid_operations = opsRotate + opsTrade + opsRelocate

    return valid_neighbor, valid_values, valid_operations


# Algorithm

def hclimbing_stepestaccent(ListofObjects, i):
    current_state = deepcopy(ListofObjects)
    current_value = stateValue(current_state)

    langkah = 0

    while True:
        choose_neighbor, values, operations = neighborList(current_state, i)

        if not choose_neighbor:
            break

        best_value = max(values)
        indexMax = values.index(best_value)

        best_neighbor = choose_neighbor[indexMax]

        if best_value > current_value:
            current_state = best_neighbor
            current_value = best_value
            langkah += 1
        else:
            break

    return current_state, current_value, langkah


def initializeHC():
    t = initialize()
    listofObjects = t[0]

    # State Awal dan State Value Awal
    initialState = deepcopy(listofObjects)
    initialValue = stateValue(listofObjects)

    print("\n")
    print("STATE AWAL")
    print("State Value Awal:", initialValue)
    print("Detail State Awal:", initialState)
    print("\n")

    bestState = deepcopy(listofObjects)
    bestValue = initialValue
    bestSteps = 0

    for i in range(len(listofObjects)):
        resultState, resultValue, steps = hclimbing_stepestaccent(listofObjects, i)

        if resultValue > bestValue:
            bestState = deepcopy(resultState)
            bestValue = resultValue
            bestSteps = steps

    print("HASIL AKHIR")
    print("Jumlah Iterasi:", bestSteps)
    print("State Value Akhir:", bestValue)
    print("Detail State Akhir:", bestState)

    visualize(bestState)

    return bestState, bestValue, bestSteps, initialState, initialValue


def testingHC():
    initializeHC()


if __name__ == "__main__":
    testingHC()




