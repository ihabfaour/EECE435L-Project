from flask import Flask
from database import init_app, db
from services.customers import customers_bp

app = Flask(__name__)

# Initialize database and migrations
init_app(app)

# Register blueprints
app.register_blueprint(customers_bp, url_prefix='/customers')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
