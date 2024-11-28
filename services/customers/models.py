from database.db_config import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    marital_status = db.Column(db.String(50), nullable=True)
    wallet_balance = db.Column(db.Float, nullable=False, default=0.0)
    role = db.Column(db.String(50), nullable=False, default='customer')  # Role: 'customer' or 'admin'

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "username": self.username,
            "age": self.age,
            "address": self.address,
            "gender": self.gender,
            "marital_status": self.marital_status,
            "wallet_balance": self.wallet_balance,
            "role": self.role
        }
