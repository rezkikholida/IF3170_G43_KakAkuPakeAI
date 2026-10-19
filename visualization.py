import matplotlib.pyplot as plt
import random

#
# VISUALIZATION FUNCTION
#


# WIP
# 1. Create truck bed (flat square with predetermined dimensions with a distinct color)

def visualize(listofObjects):
    i = 0

    x = [0]
    y = [0]
    z = [0]

    dx = [10]
    dy = [20]
    dz = [0]

    colors = ['blue']       # Truck bed is blue

    while i < len(listofObjects):
        if len(listofObjects[i].Orientation.coordinates) < 3:
            i += 1
            continue

        # Create axis (coordinates = [x, y, z] -> [width, length, height])
        x.append(listofObjects[i].Orientation.coordinates[0])
        y.append(listofObjects[i].Orientation.coordinates[1])
        z.append(listofObjects[i].Orientation.coordinates[2])

        dx.append(listofObjects[i].Dimensions.width)
        dy.append(listofObjects[i].Dimensions.length)
        dz.append(listofObjects[i].Dimensions.height)

        # Red = the package violates the truck's max width, length, or height where it is placed
        if listofObjects[i].Orientation.inside == False:
            colors.append((1, 0, 0))
            i += 1
            continue

        colors.append((random.random(), random.random(), random.random()))

        i += 1

    # Plot
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.bar3d(x, y, z, dx, dy, dz, color = colors)

    ax.set(xticklabels=[],
        yticklabels=[],
        zticklabels=[])

    plt.show()
