from flask import Blueprint, jsonify, request
from models.media import Media
from models.reaction import Reaction
from models.comment import Comment
from extensions import db

media_bp = Blueprint("media", __name__)

@media_bp.route("/<int:mid>/meta", methods=["GET"])
def media_meta(mid: int):
    m = Media.query.filter_by(id=mid).first()
    if not m or (not m.is_published and request.headers.get("X-API-Key") != __import__('config').Config.ADMIN_API_KEY):
        return jsonify({"error": "Not found"}), 404

    anon_id = (request.headers.get("X-Client-Id") or "").strip() or None
    likes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="like").scalar() or 0
    dislikes = db.session.query(db.func.count(Reaction.id)).filter_by(media_id=m.id, value="dislike").scalar() or 0
    your = None
    if anon_id:
        r = Reaction.query.filter_by(media_id=m.id, anon_id=anon_id).first()
        your = r.value if r else None
    comments_count = db.session.query(db.func.count(Comment.id)).filter_by(media_id=m.id).scalar() or 0

    return jsonify({
        "id": m.id,
        "likes": likes,
        "dislikes": dislikes,
        "yourReaction": your,
        "commentsCount": comments_count,
    })
