from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2000), nullable=False, unique=True)
    title = db.Column(db.String(500), nullable=True)
    target_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to price history
    price_history = db.relationship('PriceHistory', backref='item', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        latest_price = None
        if self.price_history:
            latest_price = sorted(self.price_history, key=lambda p: p.timestamp, reverse=True)[0].price

        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'target_price': self.target_price,
            'latest_price': latest_price,
            'created_at': self.created_at.isoformat(),
            'history': [ph.to_dict() for ph in sorted(self.price_history, key=lambda p: p.timestamp)]
        }

class PriceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'timestamp': self.timestamp.isoformat()
        }
