from datetime import datetime
from extensions import db

class Reaction(db.Model):
    __tablename__ = "reactions"
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), index=True, nullable=False)
    anon_id = db.Column(db.String(128), nullable=False, index=True)
    value = db.Column(db.String(16), nullable=False)  # like | dislike
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        db.UniqueConstraint("media_id", "anon_id", name="uq_reaction_media_anon"),
    )
