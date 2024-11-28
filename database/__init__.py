from .db_config import db, Config
from flask_migrate import Migrate
migrate = Migrate()

def init_app(app):
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
