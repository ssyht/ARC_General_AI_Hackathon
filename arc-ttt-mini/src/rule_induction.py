def _is_main_diagonal_map(a_in, a_out):
    # if out looks like transpose of in -> diagonal mirror
    if len(a_in)!=len(a_out) or len(a_in[0])!=len(a_out[0]): return False
    h, w = len(a_in), len(a_in[0])
    for i in range(h):
        for j in range(w):
            if a_out[i][j] != a_in[j][i]:
                return False
    return True

def induce_rule(task, _feats):
    """
    Heuristic:
    - If most train pairs look like transpose (mirror on main diagonal), pick op=mirror_diag
    - else try vertical mirror
    - else try 'identity' (no-op) so pipeline still runs
    """
    trains = task["train"]
    votes = {"mirror_diag":0, "mirror_vertical":0, "identity":0}
    for ex in trains:
        if _is_main_diagonal_map(ex["input"], ex["output"]):
            votes["mirror_diag"] += 1
        elif ex["input"] == ex["output"]:
            votes["identity"] += 1
        else:
            votes["mirror_vertical"] += 1
    op = max(votes, key=votes.get)
    return {"subject":"all", "op":op}

