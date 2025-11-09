from .grids import copy, shape

def _mirror_vertical(g):
    h,w = shape(g)
    out = [row[::-1] for row in g]
    return out

def _mirror_diag(g):
    h,w = shape(g)
    out = [[0]*h for _ in range(w)]
    for i in range(h):
        for j in range(w):
            out[j][i] = g[i][j]
    return out

def generate_candidates(task, rule, max_k=5):
    x = task["test"]["input"]
    cands = []
    # primary op from rule
    if rule["op"] == "mirror_diag":
        cands.append({"grid": _mirror_diag(x), "rationale": "mirror on main diagonal"})
    elif rule["op"] == "mirror_vertical":
        cands.append({"grid": _mirror_vertical(x), "rationale": "mirror vertically"})
    else:
        cands.append({"grid": copy(x), "rationale": "identity"})
    # a couple safe variants
    if len(cands) < max_k:
        cands.append({"grid": _mirror_vertical(x), "rationale": "variant: vertical mirror"})
    if len(cands) < max_k:
        cands.append({"grid": _mirror_diag(x), "rationale": "variant: diagonal mirror"})
    return cands[:max_k]
