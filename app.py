from gabor_eye import create_app


app = create_app()


if __name__ == "__main__":
    # 本番では debug=False 推奨
    app.run(host="0.0.0.0", port=8000, debug=True)
