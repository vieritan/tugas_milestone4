from app.connectors.db import db
from datetime import datetime

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    to_account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    from_account = db.relationship("Accounts", foreign_keys=[from_account_id], backref="transactions_from", lazy=True)
    to_account = db.relationship("Accounts", foreign_keys=[to_account_id], backref="transactions_to", lazy=True)

    def as_dict(self):
        return {
            "id": self.id,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
            "amount": str(self.amount),  # Convert DECIMAL to string for JSON
            "type": self.type,
            "description": self.description,
            "created_at": self.created_at
        }
