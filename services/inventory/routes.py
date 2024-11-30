from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db_config import db
from .models import Inventory
from utils import line_profile, profile_route, memory_profile
from services.customers.models import User

inventory_bp = Blueprint('inventory', __name__)

# Helper function to check admin role
def authorize_admin():
    """
    Helper function to check if the currently logged-in user has admin privileges.

    :return: A JSON response with an error message if access is forbidden, otherwise None.
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user or user.role != 'admin':
        return jsonify({"error": "Access forbidden"}), 403
    return None

@inventory_bp.route('/add', methods=['POST'])
@jwt_required()
@profile_route
@memory_profile
def add_inventory_item():
    """
    Add a new item to the inventory (admin only).

    :request json: {
        "name": "Name of the item",
        "category": "Category of the item",
        "price_per_item": "Price per unit",
        "description": "Description of the item (optional)",
        "stock_count": "Initial stock count (optional, defaults to 0)"
    }
    :return: A JSON response with a success message or an error message.
    """
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
@line_profile
@memory_profile
def deduct_stock(item_id):
    """
    Deduct a specific quantity of stock from an inventory item (admin only).

    :param item_id: ID of the inventory item to deduct stock from.
    :request json: {
        "quantity": "Quantity to deduct"
    }
    :return: A JSON response with a success message and remaining stock, or an error message.
    """
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
@line_profile
@memory_profile
def update_item(item_id):
    """
    Update details of an existing inventory item (admin only).

    :param item_id: ID of the inventory item to update.
    :request json: {
        "name": "New name (optional)",
        "category": "New category (optional)",
        "price_per_item": "New price per unit (optional)",
        "description": "New description (optional)",
        "stock_count": "New stock count (optional)"
    }
    :return: A JSON response with a success message and updated item details, or an error message.
    """
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
@profile_route
@memory_profile
def get_all_items():
    """
    Retrieve all inventory items.

    :return: A JSON response with a list of inventory items, or an error message.
    """
    try:
        # Query all items from the inventory
        items = Inventory.query.all()

        # Serialize the results into a list of dictionaries
        result = [item.to_dict() for item in items]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@inventory_bp.route('/health', methods=['GET'])
@profile_route
@memory_profile
def health_check():
    """
    Health check for the inventory service.

    :return: A JSON response indicating the status of the service.
    """
    return jsonify({"status": "Inventory service is running"}), 200
