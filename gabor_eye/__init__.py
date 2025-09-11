from __future__ import annotations

from pathlib import Path
from flask import Flask


def create_app() -> Flask:
    """Application factory.

    Configures Flask with template/static folders located at repository root
    and registers blueprints.
    """
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )

    from .routes import bp as routes_bp

    app.register_blueprint(routes_bp)
    return app

