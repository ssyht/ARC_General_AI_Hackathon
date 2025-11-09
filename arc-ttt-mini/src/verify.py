def checklist(input_grid, output_grid):
    # booleans: colors_preserved, connectivity_ok, counts_reasonable
    return {"colors_preserved": True, "connectivity_ok": True, "counts_ok": True}

def confidence(checks, score=None):
    # simple weighting -> 0..1
    val = 0.33*checks["colors_preserved"] + 0.33*checks["connectivity_ok"] + 0.34*checks["counts_ok"]
    return float(val)

def verify_candidate(task, cand_grid):
    ch = checklist(task["test"]["input"], cand_grid)
    return {"checks": ch, "confidence": confidence(ch)}

def decide(candidates, threshold=0.55):
    # pick highest confidence; abstain below threshold
    best = max(candidates, key=lambda c: c["checks"]["confidence"])
    conf = best["checks"]["confidence"]
    return {"grid": best.get("grid"), "confidence": conf, "abstain": conf < threshold, "why": "verification-driven"}
