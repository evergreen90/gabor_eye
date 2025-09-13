from __future__ import annotations

import random
from typing import Dict, List, Tuple


def ffloat(v, default):
    try:
        return float(v)
    except Exception:
        return float(default)


def fint(v, default):
    try:
        return int(v)
    except Exception:
        return int(default)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def generate_round_params(difficulty: str, size: int) -> Tuple[List[Dict], tuple[int, int]]:
    """Generate parameters for one round (16 items) and the answer pair.

    Returns (params_list, answer_pair)
    - params_list: list of 16 dicts with keys matching /api/gabor query
    - answer_pair: tuple of two indices (i, j)
    """
    size = clamp(int(size), 64, 256)

    base = {
        "size": size,
        "freq": round(random.uniform(4.0, 10.0), 2),
        "theta": round(random.uniform(0.0, 180.0), 1),
        "phase": round(random.uniform(0.0, 360.0), 1),
        "sigma": round(random.uniform(0.18, 0.30), 3),
        "gamma": round(random.uniform(0.8, 1.2), 2),
        "contrast": round(random.uniform(0.8, 1.0), 2),
        "bg": 127,
        "mode": "cos",
        "normalize": 1,
    }

    if difficulty == "easy":
        jitter = {"theta": 25, "freq": 2.0, "phase": 90, "sigma": 0.05, "gamma": 0.25}
    elif difficulty == "hard":
        jitter = {"theta": 8, "freq": 0.6, "phase": 25, "sigma": 0.015, "gamma": 0.07}
    else:  # normal
        jitter = {"theta": 15, "freq": 1.2, "phase": 45, "sigma": 0.03, "gamma": 0.12}

    idxs = list(range(16))
    random.shuffle(idxs)
    answer = (idxs[0], idxs[1])

    params_list: List[Dict] = []
    for i in range(16):
        if i in answer:
            params_list.append(base.copy())
        else:
            def jv(base_val, span, is_angle=False):
                v = base_val + random.uniform(-span, span)
                if is_angle:
                    v = v % 360.0
                return v

            p = base.copy()
            p["theta"] = round(jv(base["theta"], jitter["theta"], is_angle=False), 1)
            p["freq"] = round(clamp(jv(base["freq"], jitter["freq"]), 0.2, 32.0), 2)
            p["phase"] = round(jv(base["phase"], jitter["phase"], is_angle=True), 1)
            p["sigma"] = round(clamp(jv(base["sigma"], jitter["sigma"]), 0.02, 0.9), 3)
            p["gamma"] = round(clamp(jv(base["gamma"], jitter["gamma"]), 0.1, 3.0), 2)
            params_list.append(p)

    return params_list, answer
