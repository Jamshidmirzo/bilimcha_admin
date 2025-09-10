from flask import Blueprint, jsonify, request
from extensions import db  # ← вот так правильно
from models.media import Media  # ← импортируем конкретную модель

shorts_bp = Blueprint("shorts", __name__)

@shorts_bp.route("/shorts", methods=["GET"])
def get_shorts():
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    shorts = (
        Media.query.filter_by(is_short=True)
        .order_by(Media.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return jsonify([s.to_dict() for s in shorts]), 200
