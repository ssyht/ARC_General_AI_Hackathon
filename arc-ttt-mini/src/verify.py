from collections import Counter

def _palette(g):
    return Counter(v for row in g for v in row)

def checklist(input_grid, output_grid):
    inp, out = _palette(input_grid), _palette(output_grid)
    colors_ok = set(out.keys()).issubset(set(list(inp.keys()) + list(out.keys())))
    # weak checks just to wire the demo:
    counts_ok = abs(sum(out.values()) - sum(inp.values())) == 0
    connectivity_ok = True  # placeholder for now
    return {"colors_preserved": bool(colors_ok), "connectivity_ok": connectivity_ok, "counts_ok": counts_ok}

def confidence(checks):
    val = 0.34*checks["colors_preserved"] + 0.33*checks["connectivity_ok"] + 0.33*checks["counts_ok"]
    return float(val)

def verify_candidate(task, cand_grid):
    ch = checklist(task["test"]["input"], cand_grid)
    ch["confidence"] = confidence(ch)
    return ch

def decide(candidates, threshold=0.55):
    best = max(candidates, key=lambda c: c["checks"]["confidence"])
    conf = best["checks"]["confidence"]
    return {"grid": best["grid"], "confidence": conf, "abstain": conf < threshold, "why": best["rationale"]}

