import random
import time
import matplotlib.pyplot as plt


def fitness_function(chromosome):
    return sum(chromosome)

ukuran_populasi = 15 # ukuran populasi adalah N
jumlah_generasi = 20 # jumlah generasi adalah T, banyak iterasi yang dilakukan oleh GA
probabilitas_mutasi = 0.1
jumlah_kromosom = 10

def generate_initial_population():
    return [[random.randint(0,1) for i in range(jumlah_kromosom)] for j in range(ukuran_populasi)]

def select_parents(population, fitness_scores):
    total_fitness = sum(fitness_scores)

    if total_fitness == 0:
        selection_probs = [1 / len(population)] * len(population)
    else:
        selection_probs = [score / total_fitness for score in fitness_scores]
        
    return random.choices(population, weights=selection_probs, k=2)

def crossover(parent1, parent2):
    crossover_point = random.randint(1, jumlah_kromosom - 1)
    child1 = parent1[:crossover_point] + parent2[crossover_point:]
    child2 = parent2[:crossover_point] + parent1[crossover_point:]
    return child1, child2

def mutate(chromosome):
    mutated = chromosome.copy()
    for i in range(len(chromosome)):
        if random.random() < probabilitas_mutasi:
            mutated[i] = 1 - mutated[i]
    return mutated

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
population, fitness_data = genetic_algorithm()
best_score = max(final_scores)
best_index = final_scores.index(best_score)
best_chromosome = population[best_index]
avg_final_score = sum(final_scores) / len(final_scores)


print(f"Ukuran Populasi (Jumlah Populasi)    : {ukuran_populasi}")
print(f"Jumlah Generasi (Banyak Iterasi)     : {jumlah_generasi}")
print(f"Durasi Eksekusi      : {y - x:.4f} detik")
print(f"Solusi Awal (State Awal) :{initial_best}")
print(f"Solusi Terbaik Akhir (State Akhir) : {best_chromosome}")
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