from __future__ import annotations

import io
import json
import zipfile
from typing import Dict, List

from flask import Blueprint, jsonify, render_template, request, send_file, send_from_directory, current_app
from werkzeug.exceptions import BadRequest

from .gabor import generate_gabor_png
from .utils import clamp, fint, ffloat, generate_round_params


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
    画像フォルダ(images)からランダムに15枚＋同一画像を1枚複製して全16枚を返す。
    戻り値はファイル名配列と正解ペアのインデックス。
    """
    # List available PNGs in images directory
    images_dir = current_app.config.get("IMAGES_DIR")
    if not images_dir:
        return jsonify({"ok": False, "error": "IMAGES_DIR not configured"}), 500

    import os, random

    try:
        files = [f for f in os.listdir(images_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    except FileNotFoundError:
        return jsonify({"ok": False, "error": "images directory not found"}), 500

    # Need at least 15 distinct images
    if len(files) < 15:
        return jsonify({"ok": False, "error": "not enough images (>=15 required)"}), 400

    # Pick 15 unique, then duplicate one of them
    picks = random.sample(files, 15)
    dup = random.choice(picks)
    grid = picks + [dup]
    random.shuffle(grid)

    # Find the two positions of the duplicated filename
    idxs = [i for i, n in enumerate(grid) if n == dup]
    # In rare case shuffle makes only one occurrence (shouldn't happen), fallback recompute
    if len(idxs) != 2:
        # recompute robustly
        counts = {}
        for i, n in enumerate(grid):
            counts.setdefault(n, []).append(i)
        pair = next((v for v in counts.values() if len(v) == 2), None)
        if not pair:
            return jsonify({"ok": False, "error": "pair detection failed"}), 500
        answer = (pair[0], pair[1])
    else:
        answer = (idxs[0], idxs[1])

    return jsonify({"ok": True, "images": grid, "answer": answer})


@bp.get("/api/round_zip")
def api_round_zip():
    """16枚のガボール画像をZIPでダウンロードする。

    クエリ: difficulty, size
    同梱: meta.json（params と answer を格納）
    """
    difficulty = request.args.get("difficulty", "normal")
    size = clamp(fint(request.args.get("size", 128), 128), 64, 256)
    params_list, answer = generate_round_params(difficulty, size)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 画像
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
            zf.writestr(f"img_{i:02d}.png", png)

        # メタ情報
        meta = {"params": params_list, "answer": answer}
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False, indent=2))

    buf.seek(0)
    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name="gabor_round.zip",
    )


@bp.get("/img/<path:name>")
def serve_image(name: str):
    """Serve a pre-generated image by filename from images directory.

    Only allows files within the configured images directory.
    """
    images_dir = current_app.config.get("IMAGES_DIR")
    if not images_dir:
        raise BadRequest("IMAGES_DIR not configured")
    # Basic extension allowlist
    lower = name.lower()
    if not (lower.endswith(".png") or lower.endswith(".jpg") or lower.endswith(".jpeg")):
        raise BadRequest("unsupported file type")
    return send_from_directory(images_dir, name)
