from database.db_config import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    customer_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(50), nullable=False, default='pending')  # New field for moderation status

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "customer_username": self.customer_username,
            "rating": self.rating,
            "comment": self.comment,
            "timestamp": self.timestamp,
            "status": self.status
        }
