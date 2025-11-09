import json, os

def load_task(path):
    # path like data/arc_subset/abc123
    with open(os.path.join(path, "train.json")) as f:
        train = json.load(f)
    with open(os.path.join(path, "test.json")) as f:
        test = json.load(f)
    return {"train": train, "test": test}

def shape(grid):
    return (len(grid), len(grid[0]))

def copy(grid):
    return [row[:] for row in grid]
