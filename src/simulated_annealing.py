import math, random
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def simulated_annealing(problem, T0=50.0, alpha=0.999, T_min=1e-3):
    t0 = time.time()
    current = problem.initial_state()
    initial = problem.clone(current)
    E = problem.objective(current)
    best = problem.clone(current)
    bestE = E
    T = T0
    obj_hist, prob_hist = [], []
    stuck, rej_streak = 0, 0

    while T > T_min:
        nb = problem.neighbor(current)

        if not problem.feasible(nb):
            prob_hist.append(0.0)
            rej_streak += 1
        else:
            dE = problem.objective(nb) - E
            prob = 1.0 if dE > 0 else math.exp(dE / T)
            if random.random() < prob:
                current = nb
                E += dE
                rej_streak = 0
                if E > bestE:
                    best, bestE = problem.clone(current), E
            else:
                rej_streak += 1
            prob_hist.append(prob)
        if rej_streak == stuck_window:
            stuck += 1

        obj_hist.append(E)
        T *= alpha

    return dict(
        initial=initial,
        final=best,
        final_value=bestE,
        obj_hist=obj_hist,
        prob_hist=prob_hist,
        iterations=len(obj_hist),
        stuck=stuck,
        duration=time.time() - t0,
    )
    
def plot(res, name="sa_plot.png"):
    fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
    ax[0].plot(res["obj_hist"]); ax[0].set_title("Objective vs iterasi")
    ax[1].plot(res["prob_hist"], lw=.3); ax[1].set_title("e^(dE/T) vs iterasi")
    fig.tight_layout(); fig.savefig(name); plt.close(fig)
