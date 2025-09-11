from __future__ import annotations

import io
import random
from typing import Dict, List

from flask import Blueprint, jsonify, render_template, request, send_file
from werkzeug.exceptions import BadRequest

from .gabor import generate_gabor_png
from .utils import clamp, fint, ffloat


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.get("/api/gabor")
def api_gabor():
    # ガボール画像をPNGで返す（単機能）
    size = clamp(fint(request.args.get("size", 160), 64, 512) if request.args.get("size") else 160, 64, 512)
    cycles = clamp(ffloat(request.args.get("freq", 6), 0.2), 0.2, 32.0)  # cycles per image
    theta = clamp(ffloat(request.args.get("theta", 0), 0), 0.0, 180.0)
    phase = clamp(ffloat(request.args.get("phase", 0), 0), 0.0, 360.0)
    sigma_ratio = clamp(ffloat(request.args.get("sigma", 0.22), 0.02), 0.02, 0.9)
    gamma = clamp(ffloat(request.args.get("gamma", 1.0), 1.0), 0.1, 3.0)
    contrast = clamp(ffloat(request.args.get("contrast", 0.9), 0.9), 0.0, 1.0)
    bg = clamp(fint(request.args.get("bg", 127), 127), 0, 255)
    mode = (request.args.get("mode", "cos") or "cos").lower()
    normalize = fint(request.args.get("normalize", 1), 1)

    if mode not in ("cos", "sin"):
        raise BadRequest("mode must be 'cos' or 'sin'")

    png = generate_gabor_png(
        size=size,
        cycles=cycles,
        theta_deg=theta,
        phase_deg=phase,
        sigma_ratio=sigma_ratio,
        gamma=gamma,
        contrast=contrast,
        bg_level=bg,
        use_sine=(mode == "sin"),
        normalize=bool(normalize),
    )
    return send_file(io.BytesIO(png), mimetype="image/png")


@bp.get("/api/round")
def api_round():
    """
    1ラウンド分の16枚パラメータを返す。
    うち2枚は完全一致（answer_idxのタプルで示す）。
    難易度は 'easy' | 'normal' | 'hard' （デフォルト normal）。
    """
    difficulty = request.args.get("difficulty", "normal")
    size = clamp(fint(request.args.get("size", 128), 128), 64, 256)

    # ベース（正解ペア）のパラメータ
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

    # 難易度ごとの「紛らわしさ」（差の小ささ）
    if difficulty == "easy":
        jitter = {"theta": 25, "freq": 2.0, "phase": 90, "sigma": 0.05, "gamma": 0.25}
    elif difficulty == "hard":
        jitter = {"theta": 8, "freq": 0.6, "phase": 25, "sigma": 0.015, "gamma": 0.07}
    else:  # normal
        jitter = {"theta": 15, "freq": 1.2, "phase": 45, "sigma": 0.03, "gamma": 0.12}

    # 16位置のうち正解2枚の位置をランダムに選択
    idxs = list(range(16))
    random.shuffle(idxs)
    answer = (idxs[0], idxs[1])

    # 16枚分のパラメータを作る
    params_list: List[Dict] = []
    for i in range(16):
        if i in answer:
            params_list.append(base.copy())
        else:
            # base に微妙な差をつける
            def jv(name, base_val, span, is_angle=False):
                v = base_val + random.uniform(-span, span)
                if is_angle:
                    v = v % 360.0
                return v

            p = base.copy()
            p["theta"] = round(jv("theta", base["theta"], jitter["theta"], is_angle=False), 1)
            p["freq"] = round(clamp(jv("freq", base["freq"], jitter["freq"]), 0.2, 32.0), 2)
            p["phase"] = round(jv("phase", base["phase"], jitter["phase"], is_angle=True), 1)
            p["sigma"] = round(clamp(jv("sigma", base["sigma"], jitter["sigma"]), 0.02, 0.9), 3)
            p["gamma"] = round(clamp(jv("gamma", base["gamma"], jitter["gamma"]), 0.1, 3.0), 2)
            params_list.append(p)

    return jsonify(
        {
            "ok": True,
            "params": params_list,
            "answer": answer,  # [i, j] 形式
        }
    )

