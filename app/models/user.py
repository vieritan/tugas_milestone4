from app.connectors.db import db
from datetime import datetime

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            # "password_hash": self.password_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }