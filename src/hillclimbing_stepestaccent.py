# hillclimbing_stepestaccent.py
import random
import time
from copy import deepcopy
import matplotlib.pyplot as plt
from objects import (initialize, isOccupied, updateInside, fitting, truck)
from visualization import visualize


# Objects.py additions

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


# Neighbor generator

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


# Plot functions

def plot_objective_function(max_history, avg_history):
    plt.figure(figsize=(8, 5))
    iterations = range(len(max_history))

    plt.plot(iterations, max_history, label="Maksimum Objective Value", color="red", linewidth=2)
    plt.plot(iterations, avg_history, label="Rata-rata Objective Value", color="blue", linestyle="--", linewidth=2)

    plt.title("Perkembangan Objective Function vs Iterasi")
    plt.xlabel("Iterasi ke-")
    plt.ylabel("Nilai Objective Function (Total Weight)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Algorithm

def hclimbing_stepestaccent(ListofObjects, i):
    current_state = deepcopy(ListofObjects)
    current_value = stateValue(current_state)

    langkah = 0
    history_operations = []

    max_value_history = [current_value]
    avg_value_history = [current_value]

    while True:
        choose_neighbor, values, operations = neighborList(current_state, i)

        if not choose_neighbor:
            break

        best_value = max(values)
        indexMax = values.index(best_value)

        best_neighbor = choose_neighbor[indexMax]
        best_op = operations[indexMax]

        if best_value > current_value:
            langkah += 1
            print(f"Iterasi {langkah}")
            print(f"  - Operasi    : {best_op}")
            print(f"  - Value Lama : {current_value} -> Value Baru: {best_value}")

            current_state = best_neighbor
            current_value = best_value
            history_operations.append(best_op)

            max_val = max(values)
            avg_val = sum(values) / len(values)
            max_value_history.append(max_val)
            avg_value_history.append(avg_val)
        else:
            break

    return current_state, current_value, langkah, history_operations, max_value_history, avg_value_history


def initializeHC():
    t = initialize()
    listofObjects = t[0]

    visualize(t[0])

    population_size = len(listofObjects)

    initialState = deepcopy(listofObjects)
    initialValue = stateValue(listofObjects)

    print("State Awal=")
    print("Jumlah Populasi (Paket):", population_size)
    print("State Value Awal:", initialValue)
    print("Detail State Awal:", initialState)

    bestState = deepcopy(listofObjects)
    bestValue = initialValue
    bestSteps = 0
    bestOperations = []
    best_max_history = [initialValue]
    best_avg_history = [initialValue]

    for i in range(population_size):
        resultState, resultValue, steps, ops, max_hist, avg_hist = hclimbing_stepestaccent(listofObjects, i)

        if resultValue > bestValue:
            bestState = deepcopy(resultState)
            bestValue = resultValue
            bestSteps = steps
            bestOperations = ops
            best_max_history = max_hist
            best_avg_history = avg_hist

    print("Hasil Akhir=")
    print("Jumlah Populasi:", population_size)
    print("Jumlah Iterasi (Langkah):", bestSteps)
    print("State Value Akhir:", bestValue)
    print("Detail Operasi Terbaik:", bestOperations)
    print("Detail State Akhir:", bestState)

    plot_objective_function(best_max_history, best_avg_history)

    if bestSteps == 0:
        visualize(t[0])
    else:
        visualize(bestState)

    return bestState, bestValue, bestSteps, initialState, initialValue


def testingHC():
    initializeHC()


if __name__ == "__main__":
    testingHC()