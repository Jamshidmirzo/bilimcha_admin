from datetime import datetime
from extensions import db

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey("media.id"), index=True, nullable=False)
    anon_id = db.Column(db.String(128), nullable=True, index=True)
    username = db.Column(db.String(128), nullable=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
