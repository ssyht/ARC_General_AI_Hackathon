def induce_rule(task, feats):
    """
    Heuristic: compare train input/output to infer a simple rule card:
    - subject: {smallest|largest|all|color=X}
    - op: {mirror|rotate|translate|recolor|copy_to_corner}
    - params: axis/angle/offset/recolor_map
    """
    # Start simple: prefer mirror/rotate/recolor based on deltas between pairs
    return {"subject":"smallest","op":"mirror","axis":"vertical","recolor":{}}
