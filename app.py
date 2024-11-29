from flask import Flask
from database import init_app, db
from services.customers.routes import user_bp
from services.inventory.routes import inventory_bp
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from services.wishlist.routes import wishlist_bp
from services.sales.routes import sales_bp
from services.review.routes import reviews_bp
from services.customers.models import User
from services.review.models import Review
from services.inventory.models import Inventory
from services.wishlist.models import Wishlist
from services.review.models import Review
from services.sales.models import Sale
load_dotenv()  

app = Flask(__name__)

# Initialize database and migrations
init_app(app)

# Initialize JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY') 
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(wishlist_bp, url_prefix='/wishlist')
app.register_blueprint(sales_bp, url_prefix='/sales')
app.register_blueprint(reviews_bp, url_prefix='/reviews')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
