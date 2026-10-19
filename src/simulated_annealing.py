import math, random

def simulated_annealing(problem, T0=50.0, alpha=0.999, T_min=1e-3):
    current = problem.initial_state()
    best = problem.clone(current)
    T = T0
    obj_hist, prob_hist = [], []

    while T > T_min:
        nb = problem.neighbor(current)

        if not problem.feasible(nb):
            prob_hist.append(0.0)
        else:
            dE = problem.objective(nb) - problem.objective(current)
            prob = 1.0 if dE > 0 else math.exp(dE / T)
            if random.random() < prob:
                current = nb
                if problem.objective(current) > problem.objective(best):
                    best = problem.clone(current)
            prob_hist.append(prob)

        obj_hist.append(problem.objective(current))
        T *= alpha

    return best, obj_hist, prob_hist