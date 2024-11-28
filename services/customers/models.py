from database.db_config import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Text)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'))
    marital_status = db.Column(db.Enum('Single', 'Married', 'Divorced', 'Widowed'))
    wallet_balance = db.Column(db.DECIMAL(10, 2), default=0.00)
