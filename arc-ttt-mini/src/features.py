import numpy as np

def connected_components(grid, conn=4):
    # return list of components with pixels, color, bbox, area, centroid
    pass

def detect_symmetry(grid):
    # return {"vertical": bool, "horizontal": bool, "rot90": bool}
    pass

def extract_features(task):
    # super light: palette sizes + simple symmetry checks we might use later
    return {"n_examples": len(task["train"])}

