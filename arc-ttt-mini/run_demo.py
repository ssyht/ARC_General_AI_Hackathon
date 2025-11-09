from src.grids import load_task, show_grid
from src.features import extract_features
from src.rule_induction import induce_rule
from src.search import generate_candidates
from src.verify import verify_candidate, decide

def solve_task(task_path):
    task = load_task(task_path)  # dict with train pairs & test input
    feats = extract_features(task)
    rule = induce_rule(task, feats)  # {"subject":"smallest","op":"mirror","axis":"vertical","recolor":{"blue":"red"}}
    cands = generate_candidates(task, rule, max_k=5)  # list of {grid, rationale}
    checked = [ {**c, "checks": verify_candidate(task, c["grid"])} for c in cands ]
    final = decide(checked)  # returns {"grid":..., "confidence":..., "abstain":bool, "why":...}
    return {"rule": rule, "candidates": checked, "final": final}

if __name__ == "__main__":
    import argparse, time, json, pathlib
    p = argparse.ArgumentParser()
    p.add_argument("--task", required=True)
    args = p.parse_args()
    t0 = time.time()
    out = solve_task(args.task)
    dt = time.time() - t0
    print("\nRule card:", json.dumps(out["rule"], indent=2))
    print("\nDecision:", {"abstain": out["final"]["abstain"], "confidence": out["final"]["confidence"], "why": out["final"]["why"]})
    print(f"\nRuntime: {dt:.2f}s")
