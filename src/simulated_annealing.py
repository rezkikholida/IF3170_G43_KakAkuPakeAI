import math, random, copy, time, os, sys
import matplotlib.pyplot as plt

# Parameter yang diubah tiap variasi
T0 = 50.0
alpha = 0.999
T_min = 1e-3
stuck_window = 20
SEED = 2

def simulated_annealing(problem, T0=50.0, alpha=0.999, T_min=1e-3, stuck_window=20):
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

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_show = plt.show; plt.show = lambda *a, **k: None
import objects as O
plt.show = _show
 
TRUCK = O.truck()
W, L, H, CAP = TRUCK.Dimensions.width, TRUCK.Dimensions.length, TRUCK.Dimensions.height, TRUCK.MaxCapacity
OUTSIDE = [W, L, 0]
 
def box(p):
    c, d = p.Orientation.coordinates, p.Dimensions
    return c[0], c[1], c[2], d.width, d.length, d.height
 
 
def ov(a0, a1, b0, b1):
    return min(a1, b1) - max(a0, b0)
 
 
class TruckProblem:
    def __init__(self, seed):
        self.seed = seed
 
    def clone(self, s):
        return copy.deepcopy(s)
 
    def refresh(self, s):
        for p in s:
            O.updateInside(p, W, L, H)
 
    def objective(self, s):
        self.refresh(s)
        return sum(p.Value for p in s if p.Orientation.inside)
 
    def feasible(self, s):
        self.refresh(s)
        ins = [p for p in s if p.Orientation.inside]
        if sum(p.Weight for p in ins) > CAP:
            return False
        for i in ins:
            if O.isOccupied(ins, i)[0]:
                return False
            xi, yi, zi, wi, li, hi = box(i)
            sup = [j for j in ins if j is not i
                   and box(j)[2] + box(j)[5] == zi
                   and ov(box(j)[0], box(j)[0] + box(j)[3], xi, xi + wi) > 0
                   and ov(box(j)[1], box(j)[1] + box(j)[4], yi, yi + li) > 0]
            if zi != 0 and not sup:
                return False
            if any(j.IsFragile for j in sup):
                return False
        return True
 
    def initial_state(self):
        random.seed(self.seed)
        s, _ = O.initialize()
        for p in random.sample(s, len(s)):
            if self.feasible(s):
                break
            p.Orientation.coordinates[:] = OUTSIDE
        return s
 
    def neighbor(self, s):
        s = self.clone(s)
        m = random.choice(["swap", "move", "rotate"])
        if m == "swap":
            a, b = random.sample(s, 2)
            ca, cb = list(a.Orientation.coordinates), list(b.Orientation.coordinates)
            a.Orientation.coordinates[:], b.Orientation.coordinates[:] = cb, ca
        elif m == "move":
            p = random.choice(s)
            if p.Orientation.inside and random.random() < 0.2:
                p.Orientation.coordinates[:] = OUTSIDE
            else:
                zs = [0] + [box(q)[2] + box(q)[5] for q in s if q is not p and q.Orientation.inside]
                p.relocate([random.randint(0, max(0, W - p.Dimensions.width)),
                            random.randint(0, max(0, L - p.Dimensions.length)),
                            random.choice(zs)], s)
        else:
            random.choice(s).rotate(random.choice(["x", "y", "z"]), s)
        return s
 
if __name__ == "__main__":
    problem = TruckProblem(SEED)
    res = simulated_annealing(problem, T0, alpha, T_min, stuck_window)
 
    print(f"Parameter            : T0={T0}, alpha={alpha}, T_min={T_min}, stuck_window={stuck_window}, run={SEED}")
    print(f"Banyak Iterasi       : {res['iterations']}")
    print(f"Durasi Eksekusi      : {res['duration']:.4f} detik")
    print(f"State Awal           : {[p.id for p in res['initial'] if p.Orientation.inside]}")
    print(f"State Akhir          : {[p.id for p in res['final'] if p.Orientation.inside]}")
    print(f"Objective Awal       : {problem.objective(res['initial'])}")
    print(f"Objective Akhir      : {res['final_value']}")
    print(f"Batas atas objective : {sum(p.Value for p in res['final'])}   (total value semua paket)")
    print(f"Frekuensi stuck      : {res['stuck']}")
    print(f"Solusi valid         : {problem.feasible(res['final'])}")
 
    plot(res, f"sa_T0-{T0}_alpha-{alpha}_run{SEED}.png")
    O.visualize(res["initial"])
    O.visualize(res["final"])
