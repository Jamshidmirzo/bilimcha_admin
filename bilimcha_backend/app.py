from flask import Flask, request, jsonify, make_response
from routes.shorts import shorts_bp
from flask_cors import CORS
from config import Config
from extensions import db
import os

# create app
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    db.init_app(app)
    # CORS: разрешаем с фронта (локальная dev конфигурация)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # logging
    @app.before_request
    def log_request():
        print("\n==== NEW REQUEST ====")
        print("Path:", request.path)
        print("Method:", request.method)
        print("Headers:", dict(request.headers))
        print("Body:", request.get_data(as_text=True))
        print("=====================\n")

    # preflight response and admin key checking
    @app.before_request
    def preflight_and_auth():
        # preflight: вернём 200 с CORS заголовками
        if request.method == "OPTIONS":
            resp = make_response("", 200)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, X-Client-Id"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
            return resp

        # admin auth
        if request.path.startswith("/api/admin"):
            key = (request.headers.get("X-API-Key") or "").strip()
            if key != app.config.get("ADMIN_API_KEY"):
                return jsonify({"error": "Unauthorized, bad X-API-Key"}), 401

    # after_request: всегда добавляем CORS заголовки
    @app.after_request
    def add_cors(resp):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, X-Client-Id"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        return resp

    # register blueprints (импорт здесь, чтобы избежать циклов)
    from routes.public import public_bp
    from routes.admin import admin_bp
    from routes.media import media_bp
    from routes.comments import comments_bp
    from routes.reactions import reactions_bp
    from routes.stream import stream_bp

    app.register_blueprint(public_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(media_bp, url_prefix="/api/media")
    app.register_blueprint(comments_bp, url_prefix="/api/media")
    app.register_blueprint(reactions_bp, url_prefix="/api/media")
    app.register_blueprint(stream_bp, url_prefix="/stream")
    app.register_blueprint(shorts_bp, url_prefix="/api")

    # create db if not exists
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    # use port 5050 to match твою конфигурацию
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5050)), debug=True)
