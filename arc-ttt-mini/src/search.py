def generate_candidates(task, rule, max_k=5):
    """
    Apply rule and a few plausible variants:
      - axis in {vertical,horizontal}
      - rotate {90,180}
      - recolor permutations for small palettes
    Return [{"grid": out_grid, "rationale": "mirror vertical on smallest object"}, ...]
    """
    return []
