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

@inventory_bp.route('/<int:item_id>/deduct', methods=['POST'])
@jwt_required()
def deduct_stock(item_id):
    auth_error = authorize_admin()
    if auth_error:
        return auth_error

    try:
        # Get the item by ID
        item = Inventory.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        data = request.json
        quantity = data.get('quantity', 0)

        if quantity <= 0:
            return jsonify({"error": "Invalid quantity"}), 400

        if item.stock_count < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        # Deduct the stock
        item.stock_count -= quantity
        db.session.commit()

        return jsonify({
            "message": f"{quantity} units deducted from {item.name}",
            "remaining_stock": item.stock_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@inventory_bp.route('/<int:item_id>/update', methods=['PATCH'])
@jwt_required()
def update_item(item_id):
    auth_error = authorize_admin()
    if auth_error:
        return auth_error

    try:
        # Get the item by ID
        item = Inventory.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Update fields based on the input
        data = request.json
        if 'name' in data:
            item.name = data['name']
        if 'category' in data:
            item.category = data['category']
        if 'price_per_item' in data:
            item.price_per_item = data['price_per_item']
        if 'description' in data:
            item.description = data['description']
        if 'stock_count' in data:
            item.stock_count = data['stock_count']

        db.session.commit()

        return jsonify({"message": f"Item {item.name} updated successfully", "item": item.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@inventory_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_items():
    try:
        # Query all items from the inventory
        items = Inventory.query.all()

        # Serialize the results into a list of dictionaries
        result = [item.to_dict() for item in items]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
