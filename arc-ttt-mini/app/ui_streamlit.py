# app/ui_streamlit.py
import os, json, time, math, pathlib
from typing import List, Dict, Any, Tuple

import streamlit as st
import numpy as np
from PIL import Image

# ---- Local imports from your repo ----
# We prefer reusing solve_task() from run_demo.py if present.
try:
    from run_demo import solve_task as core_solve
except Exception:
    core_solve = None

from src.grids import load_task, shape, copy  # make sure your file is src/grids.py (plural)
from src.features import extract_features
from src.rule_induction import induce_rule
from src.search import generate_candidates
from src.verify import verify_candidate, decide


# =========================
# Utilities
# =========================

PALETTE = [
    (0, 0, 0),       # 0: black
    (0, 114, 178),   # 1: blue
    (213, 94, 0),    # 2: orange
    (204, 121, 167), # 3: purple
    (86, 180, 233),  # 4: sky
    (0, 158, 115),   # 5: green
    (240, 228, 66),  # 6: yellow
    (230, 159, 0),   # 7: amber
    (220, 50, 47),   # 8: red
    (171, 171, 171), # 9: gray
]

def to_rgb_image(grid: List[List[int]], cell_size: int = 24) -> Image.Image:
    """Convert an integer grid into a PIL image using a fixed discrete palette."""
    h, w = len(grid), len(grid[0])
    rgb = np.zeros((h, w, 3), dtype=np.uint8)
    for i in range(h):
        for j in range(w):
            idx = int(grid[i][j]) if grid[i][j] is not None else 0
            idx = max(0, min(idx, len(PALETTE)-1))
            rgb[i, j] = PALETTE[idx]
    # Upscale
    img = Image.fromarray(rgb, mode="RGB")
    img = img.resize((w * cell_size, h * cell_size), resample=Image.NEAREST)
    return img

def list_subset_tasks(root: str = "data/arc_subset") -> List[str]:
    if not os.path.isdir(root):
        return []
    out = []
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "train.json")) and os.path.exists(os.path.join(p, "test.json")):
            out.append(name)
    return out

def safe_load_task(path: str) -> Dict[str, Any]:
    try:
        return load_task(path)
    except Exception as e:
        st.error(f"Failed to load task at {path}: {e}")
        return {}

def pretty_rule(rule: Dict[str, Any]) -> str:
    # Compact printable rule card
    return json.dumps(rule, indent=2)

def solve_with_fallback(task_path: str, max_k: int, thresh: float) -> Dict[str, Any]:
    """
    Run the complete loop:
      - features -> rule -> candidates -> verify each -> decide
    Prefer run_demo.solve_task if available, else call modules directly.
    """
    if core_solve is not None:
        out = core_solve(task_path)
        # Respect current UI's threshold and candidate cap if possible
        # (core_solve may have different defaults; we'll re-decide here.)
        task = load_task(task_path)
        rechecked = []
        for c in out["candidates"]:
            # When using core_solve, candidates may already have checks; normalize:
            checks = c.get("checks", verify_candidate(task, c["grid"]))
            rechecked.append({"grid": c["grid"], "rationale": c.get("rationale", "candidate"), "checks": checks})
        rechecked = rechecked[:max_k]
        final = decide(rechecked, threshold=thresh)
        return {"rule": out["rule"], "candidates": rechecked, "final": final}

    # Manual path (using src modules)
    task = load_task(task_path)
    feats = extract_features(task)
    rule = induce_rule(task, feats)
    cands = generate_candidates(task, rule, max_k=max_k)
    checked = []
    for c in cands:
        ch = verify_candidate(task, c["grid"])
        checked.append({"grid": c["grid"], "rationale": c.get("rationale", "candidate"), "checks": ch})
    final = decide(checked, threshold=thresh)
    return {"rule": rule, "candidates": checked, "final": final}

def read_json(path: str):
    with open(path) as f:
        return json.load(f)

def col_label(s: str) -> str:
    return f":gray[{s}]"


# =========================
# UI
# =========================

st.set_page_config(page_title="ARC TTT Mini-Solver", layout="wide")
st.title("🧩 ARC Test-Time Learning Mini-Solver")

left, right = st.columns([0.33, 0.67])

with left:
    st.subheader("Task")
    task_root = "data/arc_subset"
    task_ids = list_subset_tasks(task_root)

    if not task_ids:
        st.info(
            "No tasks found in `data/arc_subset/`.\n\n"
            "Run `python tools/make_subset.py --src data/raw/ARC-AGI-2 --dst data/arc_subset --n 12` first."
        )
        st.stop()

    task_id = st.selectbox("Pick a puzzle:", task_ids, index=0)
    task_path = os.path.join(task_root, task_id)

    # Budgets & knobs
    st.subheader("Budget & Thresholds")
    max_k = st.slider("Max candidates (search width)", min_value=1, max_value=10, value=5, step=1)
    thresh = st.slider("Confidence threshold (abstain below)", min_value=0.0, max_value=1.0, value=0.55, step=0.01)

    st.markdown("---")
    st.subheader("Examples (train pairs)")
    task = safe_load_task(task_path)
    train_pairs = task.get("train", [])
    if train_pairs:
        for idx, pair in enumerate(train_pairs, start=1):
            st.caption(f"Example {idx}")
            a, b = pair["input"], pair["output"]
            i1, i2 = to_rgb_image(a), to_rgb_image(b)
            c1, c2 = st.columns(2)
            with c1:
                st.image(i1, caption=col_label("input"), use_column_width=True)
            with c2:
                st.image(i2, caption=col_label("output"), use_column_width=True)
    else:
        st.write("No training pairs found.")

    st.markdown("---")
    st.subheader("Test input")
    test_input = task.get("test", {}).get("input")
    if test_input is not None:
        st.image(to_rgb_image(test_input), caption=col_label("test input"), use_column_width=True)

    # Solve button
    st.markdown("---")
    run_btn = st.button("⚡ Quick Learn + Solve", use_container_width=True)

with right:
    if 'last_result' not in st.session_state:
        st.session_state['last_result'] = None
        st.session_state['last_task'] = None

    if run_btn:
        t0 = time.time()
        result = solve_with_fallback(task_path, max_k=max_k, thresh=thresh)
        dt = time.time() - t0
        st.session_state['last_result'] = (result, dt)
        st.session_state['last_task'] = task_id

    # Show latest result
    payload = st.session_state['last_result']
    if payload and st.session_state['last_task'] == task_id:
        result, dt = payload

        st.subheader("Rule Card (inferred)")
        st.code(pretty_rule(result["rule"]), language="json")

        st.subheader("Candidates")
        cands = result["candidates"]
        if not cands:
            st.info("No candidates generated.")
        else:
            # Grid gallery
            ncols = 3
            rows = math.ceil(len(cands) / ncols)
            idx = 0
            for _ in range(rows):
                cols = st.columns(ncols)
                for c in cols:
                    if idx >= len(cands):
                        break
                    cand = cands[idx]
                    img = to_rgb_image(cand["grid"])
                    c.image(img, use_column_width=True)
                    # Checks & confidence
                    ch = cand["checks"]
                    conf = ch.get("confidence", 0.0)
                    c.caption(f"**{cand['rationale']}** · confidence: `{conf:.2f}`")
                    with c.expander("checks"):
                        st.write({
                            "colors_preserved": ch.get("colors_preserved", None),
                            "connectivity_ok": ch.get("connectivity_ok", None),
                            "counts_ok": ch.get("counts_ok", None),
                        })
                    idx += 1

        st.markdown("---")
        st.subheader("Decision")
        final = result["final"]
        dcols = st.columns([0.55, 0.45])
        with dcols[0]:
            st.image(to_rgb_image(final["grid"]), caption="final grid", use_column_width=True)
        with dcols[1]:
            st.metric(label="Confidence", value=f"{final['confidence']:.2f}")
            if final["abstain"]:
                st.warning("Abstained (below threshold).")
            else:
                st.success("Answer submitted.")
            st.caption(f"Why: {final.get('why','')}")

        st.markdown("---")
        st.subheader("Runtime & Budget")
        st.write({
            "runtime_seconds": round(dt, 3),
            "max_candidates": max_k,
            "threshold": thresh
        })

    else:
        st.info("Pick a task on the left and click **Quick Learn + Solve** to see candidates and a final decision.")


# =========================
# Footer
# =========================
st.markdown("---")
st.caption("ARC TTT Mini-Solver — learns during the test, tries a few explainable options, verifies, then answers or abstains.")
