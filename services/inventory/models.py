from database.db_config import db

class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name of the item
    category = db.Column(db.String(50), nullable=False)  # Category (food, clothes, etc.)
    price_per_item = db.Column(db.Float, nullable=False)  # Price per item
    description = db.Column(db.String(255))  # Item description
    stock_count = db.Column(db.Integer, nullable=False, default=0)  # Available items in stock

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price_per_item": self.price_per_item,
            "description": self.description,
            "stock_count": self.stock_count,
        }
