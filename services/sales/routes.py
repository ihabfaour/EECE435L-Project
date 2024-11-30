from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db_config import db
from .models import Sale
from services.customers.models import User
from services.inventory.models import Inventory
from utils import profile_route, line_profile, memory_profile

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/display', methods=['GET'])
@profile_route  # Adding the route profiler
@line_profile  # Adding the line profiler (optional, for more granular profiling)
@memory_profile  # Adding memory profiling
def display_goods():
    """
    Display a list of all available goods.

    :return: JSON response containing a list of goods with their names and prices,
             or an error message in case of failure.
    """
    try:
        items = Inventory.query.all()
        result = [{"name": item.name, "price": item.price_per_item} for item in items]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sales_bp.route('/details/<int:item_id>', methods=['GET'])
@profile_route
@memory_profile
def get_good_details(item_id):
    """
    Get details of a specific good.

    :param item_id: ID of the good to retrieve details for.
    :return: JSON response containing the item's details, or an error message.
    """
    try:
        item = Inventory.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sales_bp.route('/sale', methods=['POST'])
@jwt_required()
@profile_route
@line_profile
@memory_profile
def make_sale():
    """
    Make a sale for a specified product and quantity.

    :request json: {
        "product_id": int,  # ID of the product to purchase
        "quantity": int     # Quantity to purchase
    }
    :return: JSON response with the sale details or an error message.
    """
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if not product_id or not quantity or quantity <= 0:
            return jsonify({"error": "Invalid product or quantity"}), 400

        item = Inventory.query.get(product_id)
        if not item:
            return jsonify({"error": "Product not found"}), 404
        if item.stock_count < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        total_price = item.price_per_item * quantity
        if user.wallet_balance < total_price:
            return jsonify({"error": "Insufficient wallet balance"}), 400

        # Deduct from customer wallet
        user.wallet_balance -= total_price
        # Deduct stock
        item.stock_count -= quantity
        # Record the sale
        sale = Sale(
            customer_username=current_user,
            product_id=item.id,
            product_name=item.name,
            quantity=quantity,
            total_price=total_price
        )
        db.session.add(sale)
        db.session.commit()

        return jsonify({
            "message": "Sale completed successfully",
            "sale_details": sale.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@sales_bp.route('/history', methods=['GET'])
@jwt_required()
@profile_route
@memory_profile
def get_purchase_history():
    """
    Retrieve the purchase history for the logged-in customer.

    :return: JSON response containing a list of past purchases or an error message.
    """
    try:
        current_user = get_jwt_identity()
        sales = Sale.query.filter_by(customer_username=current_user).all()
        result = [sale.to_dict() for sale in sales]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
