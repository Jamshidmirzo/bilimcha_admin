from datetime import datetime
from extensions import db

class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True)
    youtube_id = db.Column(db.String(64), nullable=False, index=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)
    thumbnail_url = db.Column(db.String(1024))
    is_short = db.Column(db.Boolean, default=False, index=True)
    is_published = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "youtubeId": self.youtube_id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "thumbnailUrl": self.thumbnail_url or f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg",
            "isShort": self.is_short,
            "isPublished": self.is_published,
            "createdAt": (self.created_at.isoformat() + "Z") if self.created_at else None,
            "playbackUrl": f"/stream/{self.youtube_id}",
        }
