import json, os, random, argparse, shutil
random.seed(7)

def to_subset(src_dir, dst_dir, n=10, use_eval=False):
    os.makedirs(dst_dir, exist_ok=True)
    # ARC-AGI-2 layout:
    # data/ARC-AGI-2_public_train/*.json  or  data/ARC-AGI-2_public_eval/*.json
    split = "ARC-AGI-2_public_eval" if use_eval else "ARC-AGI-2_public_train"
    src = os.path.join(src_dir, "data", split)
    files = [f for f in os.listdir(src) if f.endswith(".json")]
    random.shuffle(files)
    for fname in files[:n]:
        tid = os.path.splitext(fname)[0]
        with open(os.path.join(src, fname)) as f:
            task = json.load(f)
        outdir = os.path.join(dst_dir, tid)
        os.makedirs(outdir, exist_ok=True)
        # Your pipeline expects separate train.json and test.json (first test item)
        with open(os.path.join(outdir, "train.json"), "w") as f:
            json.dump(task["train"], f)
        with open(os.path.join(outdir, "test.json"), "w") as f:
            json.dump(task["test"][0], f)
    print(f"Wrote {min(n,len(files))} tasks to {dst_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="data/raw/ARC-AGI-2")
    ap.add_argument("--dst", default="data/arc_subset")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--use_eval", action="store_true")
    args = ap.parse_args()
    to_subset(args.src, args.dst, args.n, args.use_eval)
