#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from gabor_eye.gabor import generate_gabor_png
from gabor_eye.utils import generate_round_params


def main():
    ap = argparse.ArgumentParser(description="Generate 16 Gabor images and meta.json")
    ap.add_argument("--difficulty", default="normal", choices=["easy", "normal", "hard"], help="difficulty")
    ap.add_argument("--size", type=int, default=128, help="image size (64..256)")
    ap.add_argument("--outdir", default="output", help="output directory")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    params_list, answer = generate_round_params(args.difficulty, args.size)

    for i, p in enumerate(params_list):
        png = generate_gabor_png(
            size=p["size"],
            cycles=p["freq"],
            theta_deg=p["theta"],
            phase_deg=p["phase"],
            sigma_ratio=p["sigma"],
            gamma=p["gamma"],
            contrast=p["contrast"],
            bg_level=p["bg"],
            use_sine=(p["mode"].lower() == "sin"),
            normalize=bool(p["normalize"]),
        )
        (outdir / f"img_{i:02d}.png").write_bytes(png)

    meta = {"params": params_list, "answer": answer}
    (outdir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved 16 images and meta.json to: {outdir}")


if __name__ == "__main__":
    main()

