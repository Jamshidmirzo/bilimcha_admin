from flask import Blueprint, request, jsonify
from extensions import db
from models.media import Media
from models.comment import Comment
from models.reaction import Reaction
from services.youtube import fetch_meta
from config import Config

admin_bp = Blueprint("admin", __name__)

def require_api_key():
    key = (request.headers.get("X-API-Key") or "").strip()
    if key != Config.ADMIN_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return None

def _paginated(q):
    limit = max(1, min(100, int(request.args.get("limit", "50"))))
    offset = max(0, int(request.args.get("offset", "0")))
    return q.offset(offset).limit(limit).all()

# LIST
@admin_bp.route("/videos", methods=["GET"])
def admin_videos():
    if err := require_api_key():
        return err
    q = Media.query.filter_by(is_short=False)
    search = (request.args.get("q") or "").strip()
    if search:
        like = f"%{search}%"
        q = q.filter(db.or_(Media.title.ilike(like), Media.youtube_id.ilike(like)))
    q = q.order_by(Media.created_at.desc())
    rows = _paginated(q)
    return jsonify([m.to_dict() for m in rows])

@admin_bp.route("/shorts", methods=["GET"])
def admin_shorts():
    if err := require_api_key():
        return err
    q = Media.query.filter_by(is_short=True).order_by(Media.created_at.desc())
    rows = _paginated(q)
    return jsonify([m.to_dict() for m in rows])

# CREATE
@admin_bp.route("/videos", methods=["POST"])
def admin_create_video():
    if err := require_api_key():
        return err
    data = request.get_json(force=True) or {}
    youtube_id = (data.get("youtubeId") or "").strip()
    autofetch = data.get("autofetch", True)
    if not youtube_id:
        return jsonify({"error": "youtubeId required"}), 400
    m = Media(youtube_id=youtube_id, is_short=False)
    if autofetch:
        try:
            meta = fetch_meta(youtube_id)
            m.title = meta.get("title")
            m.description = meta.get("description")
            m.duration = meta.get("duration")
            m.thumbnail_url = meta.get("thumbnail")
        except Exception as e:
            # не критично — создаём запись без меты
            print("meta fetch failed:", e)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201

@admin_bp.route("/shorts", methods=["POST"])
def admin_create_short():
    if err := require_api_key():
        return err
    data = request.get_json(force=True) or {}
    youtube_id = (data.get("youtubeId") or "").strip()
    autofetch = data.get("autofetch", True)
    if not youtube_id:
        return jsonify({"error": "youtubeId required"}), 400
    m = Media(youtube_id=youtube_id, is_short=True)
    if autofetch:
        try:
            meta = fetch_meta(youtube_id)
            m.title = meta.get("title")
            m.description = meta.get("description")
            m.duration = meta.get("duration")
            m.thumbnail_url = meta.get("thumbnail")
        except Exception as e:
            print("meta fetch failed:", e)
    db.session.add(m)
    db.session.commit()
    return jsonify(m.to_dict()), 201

# UPDATE (patch)
@admin_bp.route("/videos/<int:mid>", methods=["PATCH"])
def admin_update_video(mid: int):
    if err := require_api_key():
        return err
    data = request.get_json(force=True) or {}
    m = Media.query.filter_by(id=mid, is_short=False).first()
    if not m:
        return jsonify({"error": "Not found"}), 404
    if "title" in data:
        m.title = data["title"]
    if "isPublished" in data:
        m.is_published = bool(data["isPublished"])
    if data.get("autofetchMeta"):
        try:
            meta = fetch_meta(m.youtube_id)
            m.title = meta.get("title")
            m.description = meta.get("description")
            m.duration = meta.get("duration")
            m.thumbnail_url = meta.get("thumbnail")
        except Exception as e:
            print("autofetch failed:", e)
    db.session.commit()
    return jsonify(m.to_dict())

@admin_bp.route("/shorts/<int:mid>", methods=["PATCH"])
def admin_update_short(mid: int):
    if err := require_api_key():
        return err
    data = request.get_json(force=True) or {}
    m = Media.query.filter_by(id=mid, is_short=True).first()
    if not m:
        return jsonify({"error": "Not found"}), 404
    if "title" in data:
        m.title = data["title"]
    if "isPublished" in data:
        m.is_published = bool(data["isPublished"])
    if data.get("autofetchMeta"):
        try:
            meta = fetch_meta(m.youtube_id)
            m.title = meta.get("title")
            m.description = meta.get("description")
            m.duration = meta.get("duration")
            m.thumbnail_url = meta.get("thumbnail")
        except Exception as e:
            print("autofetch failed:", e)
    db.session.commit()
    return jsonify(m.to_dict())

# DELETE
@admin_bp.route("/videos/<int:mid>", methods=["DELETE"])
def admin_delete_video(mid: int):
    if err := require_api_key():
        return err
    m = Media.query.filter_by(id=mid, is_short=False).first()
    if not m:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({"ok": True})

@admin_bp.route("/shorts/<int:mid>", methods=["DELETE"])
def admin_delete_short(mid: int):
    if err := require_api_key():
        return err
    m = Media.query.filter_by(id=mid, is_short=True).first()
    if not m:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(m)
    db.session.commit()
    return jsonify({"ok": True})

# OVERVIEW
@admin_bp.route("/overview", methods=["GET"])
def admin_overview():
    if err := require_api_key():
        return err
    total = Media.query.count()
    videos = Media.query.filter_by(is_short=False).count()
    shorts = Media.query.filter_by(is_short=True).count()
    published = Media.query.filter_by(is_published=True).count()
    likes = db.session.query(db.func.count(Reaction.id)).scalar() or 0
    dislikes = db.session.query(db.func.count(Reaction.id)).filter(Reaction.value == "dislike").scalar() or 0
    last_comments = Comment.query.order_by(Comment.created_at.desc()).limit(10).all()
    return jsonify({
        "counts": {
            "total": total,
            "videos": videos,
            "shorts": shorts,
            "published": published,
            "likes": likes,
            "dislikes": dislikes
        },
        "lastComments": [ {"id": c.id, "username": c.username or "Anon", "text": c.text, "createdAt": c.created_at.isoformat()+"Z"} for c in last_comments ]
    })
