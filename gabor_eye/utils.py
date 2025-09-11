from __future__ import annotations


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

