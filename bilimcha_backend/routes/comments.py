from flask import Blueprint, request, jsonify
from models.comment import Comment
from models.media import Media
from extensions import db

comments_bp = Blueprint("comments", __name__)

@comments_bp.route("/<int:mid>/comments", methods=["GET"])
def media_comments_list(mid: int):
    m = Media.query.filter_by(id=mid).first()
    if not m or (not m.is_published and request.headers.get("X-API-Key") != __import__('config').Config.ADMIN_API_KEY):
        return jsonify({"error": "Not found"}), 404

    limit = max(1, min(100, int(request.args.get("limit", "30"))))
    offset = max(0, int(request.args.get("offset", "0")))

    q = Comment.query.filter_by(media_id=m.id).order_by(Comment.created_at.desc())
    rows = q.offset(offset).limit(limit).all()
    return jsonify([
        {
            "id": c.id,
            "username": c.username or "Anon",
            "text": c.text,
            "createdAt": c.created_at.isoformat() + "Z",
        }
        for c in rows
    ])

@comments_bp.route("/<int:mid>/comments", methods=["POST"])
def media_comments_add(mid: int):
    m = Media.query.filter_by(id=mid).first()
    if not m or (not m.is_published and request.headers.get("X-API-Key") != __import__('config').Config.ADMIN_API_KEY):
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400
    username = (data.get("username") or "").strip() or None
    anon_id = (request.headers.get("X-Client-Id") or "").strip() or None

    c = Comment(media_id=m.id, anon_id=anon_id, username=username, text=text)
    db.session.add(c)
    db.session.commit()

    return jsonify({
        "ok": True,
        "comment": {
            "id": c.id,
            "username": c.username or "Anon",
            "text": c.text,
            "createdAt": c.created_at.isoformat() + "Z"
        }
    }), 201
