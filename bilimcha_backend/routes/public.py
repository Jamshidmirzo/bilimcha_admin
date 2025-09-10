from flask import Blueprint, jsonify, request
from extensions import db
from models.media import Media

public_bp = Blueprint("public", __name__)

def _list_media_query(is_short: bool):
    q = Media.query.filter_by(is_short=is_short, is_published=True)
    search = (request.args.get("q") or "").strip()
    if search:
        like = f"%{search}%"
        q = q.filter(db.or_(Media.title.ilike(like), Media.youtube_id.ilike(like)))
    return q.order_by(Media.created_at.desc())

def _paginated(q):
    limit = max(1, min(100, int(request.args.get("limit", "50"))))
    offset = max(0, int(request.args.get("offset", "0")))
    return q.offset(offset).limit(limit).all()

@public_bp.route("/videos", methods=["GET"])
def videos_list_public():
    rows = _paginated(_list_media_query(is_short=False))
    return jsonify([m.to_dict() for m in rows])

@public_bp.route("/shorts", methods=["GET"])
def shorts_list_public():
    rows = _paginated(_list_media_query(is_short=True))
    return jsonify([m.to_dict() for m in rows])

@public_bp.route("/videos/<int:mid>", methods=["GET"])
def videos_get_public(mid):
    m = Media.query.filter_by(id=mid, is_short=False, is_published=True).first()
    if not m:
        return jsonify({"error": "Not found"}), 404
    return jsonify(m.to_dict())

@public_bp.route("/shorts/<int:mid>", methods=["GET"])
def shorts_get_public(mid):
    m = Media.query.filter_by(id=mid, is_short=True, is_published=True).first()
    if not m:
        return jsonify({"error": "Not found"}), 404
    return jsonify(m.to_dict())
