import time, csv
from run_demo import solve_task

def evaluate(task_paths, results_csv="results.csv"):
    ok = 0
    t_total = 0.0
    attempts = []
    with open(results_csv, "a", newline="") as f:
        w = csv.writer(f)
        for p in task_paths:
            t0 = time.time()
            out = solve_task(p)
            dt = time.time() - t0
            t_total += dt
            # TODO: compute exact match vs ground truth here
            exact = 0
            tries = len(out["candidates"])
            attempts.append(tries)
            w.writerow([p, exact, out["final"]["abstain"], tries, f"{dt:.2f}"])
    return {"acc": ok/len(task_paths), "avg_time": t_total/len(task_paths), "avg_attempts": sum(attempts)/len(attempts)}
