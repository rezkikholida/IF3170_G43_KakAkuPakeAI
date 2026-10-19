import copy
import random
import time
import matplotlib.pyplot as plt

from objects import initialize, pushAbove

# Inisialisasi data paket dan truk
base_packages, my_truck = initialize()

def fitness_function(chromosome):
    total_value = 0
    for pkg in chromosome:
        if pkg.Orientation.inside:
            total_value += pkg.Value
    return total_value

ukuran_populasi = 15 # ukuran populasi adalah N
jumlah_generasi = 20 # jumlah generasi adalah T, banyak iterasi yang dilakukan oleh GA
probabilitas_mutasi = 0.1
jumlah_kromosom = 10

def fix_positions(chromosome): # biar ga aneh output paketnya
  for pkg in chromosome:
    pushAbove(chromosome, pkg)
    pkg.retrace(chromosome)
  return chromosome

def generate_initial_population():
    population = []
    for _ in range(ukuran_populasi):
        individual = copy.deepcopy(base_packages)

        for pkg in individual:
            pkg.rotate(random.choice(["x", "y", "z"]), individual)
            pkg.relocate([random.randint(0,10), random.randint(0,20), random.randint(0,5)], individual)
            individual = fix_positions(individual)
        population.append(individual)
    return population

def select_parents(population, fitness_scores):
    total_fitness = sum(fitness_scores)

    if total_fitness == 0:
        selection_probs = [1 / len(population)] * len(population)
    else:
        selection_probs = [score / total_fitness for score in fitness_scores]
        
    return random.choices(population, weights=selection_probs, k=2)

def crossover(parent1, parent2):
    child1 = copy.deepcopy(parent1)
    child2 = copy.deepcopy(parent2)

    if len(parent1) > 1:
        crossover_point = random.randint(1, len(parent1) - 1)
        for i in range(crossover_point, len(parent1)):
            child1[i].Orientation = copy.deepcopy(parent2[i].Orientation)
            child2[i].Orientation = copy.deepcopy(parent1[i].Orientation)
            child1[i].retrace(child1)
            child2[i].retrace(child2)
    return fix_positions(child1), fix_positions(child2)


def mutate(chromosome):
    mutated = copy.deepcopy(chromosome)
    for pkg in mutated: 
        if random.random() < probabilitas_mutasi:
            aksi = random.choice(["rotate", "trade", "relocate"])
            if aksi == "rotate":
                pkg.rotate(random.choice(["x", "y", "z"]), mutated)
            elif aksi == "trade" and len(mutated) > 1:
                target = random.choice([p for p in mutated if p!= pkg])
                pkg.trade(target, mutated)
            elif aksi == "relocate":
                pkg.relocate([random.randint(0, 10), random.randint(0, 20), random.randint(0,5),], mutated,)
    return fix_positions(mutated)

def genetic_algorithm():
    population = generate_initial_population()

    initial_scores = [fitness_function(chromosome) for chromosome in population]
    initial_best = population[initial_scores.index(max(initial_scores))]

    best_fitness_over_time = []
    average_fitness_over_time = []

    for generation in range(jumlah_generasi):
        fitness_scores = [fitness_function(chromosome) for chromosome in population]
        best_fitness_over_time.append(max(fitness_scores))
        average_fitness_over_time.append(sum(fitness_scores) / len(fitness_scores))

        new_population = []
        for _ in range(ukuran_populasi // 2):
            parent1, parent2 = select_parents(population, fitness_scores = [fitness_function(chromosome) for chromosome in population])
            child1, child2 = crossover(parent1, parent2)      
            child1 = mutate(child1)
            child2 = mutate(child2)
            new_population.extend([child1, child2])

        population = new_population

    return population, [best_fitness_over_time, average_fitness_over_time, initial_best]

x = time.time()
population, fitness_data = genetic_algorithm()
y = time.time()
print("Execution time:", y - x, "seconds")

final_scores = [fitness_function(chromosome) for chromosome in population]

initial_best = fitness_data[2]

best_score = max(final_scores)
best_index = final_scores.index(best_score)
best_chromosome = population[best_index]
avg_final_score = sum(final_scores) / len(final_scores)


print(f"Ukuran Populasi (Jumlah Populasi)    : {ukuran_populasi}")
print(f"Jumlah Generasi (Banyak Iterasi)     : {jumlah_generasi}")
print(f"Durasi Eksekusi      : {y - x:.4f} detik")
print(f"Solusi Awal (State Awal) :{[p.id for p in initial_best]}")
print(f"Solusi Terbaik Akhir (State Akhir) : {[p.id for p in best_chromosome]}")
print(f"Fitness Terbaik (Nilai Objective Function Akhir)     : {best_score} / {jumlah_kromosom}")
print(f"Fitness Rata-Rata (Nilai Objective Function Rata-Rata)    : {avg_final_score:.2f}")


plt.figure(figsize=(8, 4.5))
plt.plot(fitness_data[0], label="Fitness Maksimum", color="#386641", linewidth=2)
plt.plot(fitness_data[1], label="Fitness Rata-Rata", color="#a3b18a", linestyle="--")
plt.title("Perkembangan Fitness Over Generations")
plt.xlabel("Generasi")
plt.ylabel("Fitness")
plt.legend()
plt.grid(True)
plt.show()