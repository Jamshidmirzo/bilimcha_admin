from flask import Blueprint, request, jsonify
from models.reaction import Reaction
from models.media import Media
from extensions import db

reactions_bp = Blueprint("reactions", __name__)

def get_client_id():
    return (request.headers.get("X-Client-Id") or "").strip() or None

@reactions_bp.route("/<int:mid>/react", methods=["POST"])
def media_react(mid: int):
    m = Media.query.filter_by(id=mid).first()
    if not m or (not m.is_published and request.headers.get("X-API-Key") != __import__('config').Config.ADMIN_API_KEY):
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action")
    anon_id = get_client_id()
    if not anon_id:
        return jsonify({"error": "X-Client-Id header required"}), 400
    if action not in ("like", "dislike", "clear"):
        return jsonify({"error": "action must be like|dislike|clear"}), 400

    r = Reaction.query.filter_by(media_id=m.id, anon_id=anon_id).first()

    if action == "clear":
        if r:
            db.session.delete(r)
            db.session.commit()
        likes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="like").scalar() or 0
        dislikes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="dislike").scalar() or 0
        return jsonify({"ok": True, "likes": likes, "dislikes": dislikes, "yourReaction": None})

    if not r:
        r = Reaction(media_id=m.id, anon_id=anon_id, value=action)
        db.session.add(r)
    else:
        if r.value == action:
            db.session.delete(r)
            db.session.commit()
            likes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="like").scalar() or 0
            dislikes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="dislike").scalar() or 0
            return jsonify({"ok": True, "likes": likes, "dislikes": dislikes, "yourReaction": None})
        r.value = action

    db.session.commit()
    likes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="like").scalar() or 0
    dislikes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="dislike").scalar() or 0
    return jsonify({"ok": True, "likes": likes, "dislikes": dislikes, "yourReaction": action})
