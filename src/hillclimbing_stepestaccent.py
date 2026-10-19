#deretan bukit
import random
import time
import matplotlib.pyplot as plt

# ini objek ngasal sebelum di ubah ke objek soal
class DummyState:
    def __init__(self, value):
        self.value = value

    def get_score(self):
        # Contoh fungsi nilai objective (-x^2 + 10x)
        return -1 * (self.value ** 2) + (10 * self.value)

    def get_neighbors(self):
        # Menghasilkan tetangga dummy (geser -1 dan +1)
        return [DummyState(self.value - 1), DummyState(self.value + 1)]

# Definisi initial_state random
initial_state = DummyState(value= random.randint(-10,10))
#fungsi cari neighboor
def hclimbing_stepestaccent (current_state):
    return current_state.get_neighbors()
    
# fungsi utama steepest accent with constraint
def steepest_accent_constrained(now_state):
    current_value = now_state
    langkah = 1

    history = [current_value.get_score()] #catat nilai awal

    while True:
        choose_neighboor = hclimbing_stepestaccent (current_value)
        if not choose_neighboor:
            break
        best_neighboor = max(choose_neighboor, key=lambda idx: idx.get_score())

        if best_neighboor.get_score() > current_value.get_score():
            current_value = best_neighboor
            langkah+= 1
            history.append(current_value.get_score())
        else:
            break
    return current_value, langkah, history

start_time = time.time()
puncak, total_iterations, history = steepest_accent_constrained(initial_state)
end_time = time.time()


print("Starting position:", initial_state)
print("Local max state:", puncak)
print("Value at Local max:", puncak.get_score())
print("Execution time:", end_time - start_time, "seconds")
print("Total iterations:", total_iterations)

# Plot the optimization process
plt.plot(history)
plt.title("Steepest Ascent Hill Climbing")
plt.xlabel("iterasi ke-")
plt.ylabel("nilai objektif")
plt.show()




