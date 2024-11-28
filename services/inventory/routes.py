from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db_config import db
from .models import Inventory
from services.customers.models import User

inventory_bp = Blueprint('inventory', __name__)

# Helper function to check admin role
def authorize_admin():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user or user.role != 'admin':
        return jsonify({"error": "Access forbidden"}), 403
    return None


@inventory_bp.route('/add', methods=['POST'])
@jwt_required()
def add_inventory_item():
    auth_error = authorize_admin()  # Only admins can add inventory
    if auth_error:
        return auth_error

    try:
        data = request.json
        new_item = Inventory(
            name=data['name'],
            category=data['category'],
            price_per_item=data['price_per_item'],
            description=data.get('description', ''),
            stock_count=data.get('stock_count', 0)
        )
        db.session.add(new_item)
        db.session.commit()

        return jsonify({"message": "Item added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
