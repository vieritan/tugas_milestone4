from app.connectors.db import db
from datetime import datetime

class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type = db.Column(db.String(255), nullable=False)
    account_number = db.Column(db.String(255), unique=True, nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("Users", backref="accounts", lazy=True)

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_type": self.account_type,
            "account_number": self.account_number,
            "balance": str(self.balance),  # Convert DECIMAL to string for JSON
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
