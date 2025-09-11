# Gabor Eye 3分チャレンジ（Flask版）

4×4=16枚から同一のガボールパッチを探す 3 分チャレンジ。

## 構成（リファクタ後）
- `gabor_eye/`: Flask アプリ本体
  - `__init__.py`: `create_app()` ファクトリ
  - `routes.py`: 画面ルートと API (`/api/gabor`, `/api/round`)
  - `gabor.py`: ガボール生成ロジック
  - `utils.py`: ヘルパー（型安全なパースや clamp など）
- `templates/`, `static/`: UI 一式
- `app.py`: ローカル実行エントリ

## 必要環境
- Python 3.13.5（pyenv の場合: `.python-version` 参照）

## セットアップ
```bash
# 推奨: pyenv 等で 3.13.5 を有効化
# macOS 例: pyenv install 3.13.5 && pyenv local 3.13.5

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python app.py
# ブラウザ: http://localhost:8000
```

### トラブルシューティング
- `.venv` が別バージョン（3.12 など）で作られている場合は作り直してください。
  ```bash
  rm -rf .venv
  pyenv local 3.13.5  # 必要に応じて
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  ```

### Python 3.13 対応メモ
- 依存パッケージを Python 3.13 対応版に更新しました。
  - `numpy>=2.1.2,<3`
  - `Pillow>=11,<12`
  - `Flask>=3,<4`
  既存の仮想環境でエラーが出る場合は、上記の手順で環境を作り直してください。
