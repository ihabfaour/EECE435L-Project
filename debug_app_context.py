from app import app
from database import db

with app.app_context():
    print(db.engine.url)
