from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db_config import db
from services.wishlist.models import Wishlist
from services.inventory.models import Inventory
from services.customers.models import User
from utils import profile_route, line_profile

wishlist_bp = Blueprint('wishlist', __name__)

# Helper function to check customer role
def authorize_customer():
    """
    Helper function to check if the currently logged-in user has customer privileges.

    :return: A JSON response with an error message if access is forbidden, otherwise None.
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user or user.role != 'customer':
        return jsonify({"error": "Access forbidden"}), 403
    return None

@wishlist_bp.route('/add', methods=['POST'])
@jwt_required()
@profile_route
def add_to_wishlist():
    """
    Add an item to the user's wishlist (customer only).

    :request json: {
        "item_id": "ID of the inventory item to add"
    }
    :return: A JSON response with a success message, or an error message if the item is already in the wishlist or not found.
    """
    auth_error = authorize_customer()
    if auth_error:
        return auth_error

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    data = request.json
    item_id = data.get('item_id')

    # Check if the item exists in inventory
    item = Inventory.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    # Check if the item is already in the user's wishlist
    existing_entry = Wishlist.query.filter_by(user_id=user.id, item_id=item_id).first()
    if existing_entry:
        return jsonify({"message": f"'{item.name}' is already in your wishlist"}), 200

    # Add item to wishlist
    wishlist_entry = Wishlist(user_id=user.id, item_id=item_id)
    db.session.add(wishlist_entry)
    db.session.commit()

    return jsonify({"message": f"'{item.name}' has been added to your wishlist"}), 201


@wishlist_bp.route('/', methods=['GET'])
@jwt_required()
@line_profile
def view_wishlist():
    """
    View the items in the user's wishlist (customer only).

    :return: A JSON response with a list of wishlist items, or an error message if access is forbidden.
    """
    auth_error = authorize_customer()
    if auth_error:
        return auth_error

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    # Fetch wishlist items for the user
    wishlist = Wishlist.query.filter_by(user_id=user.id).all()
    result = [entry.to_dict() for entry in wishlist]

    return jsonify(result), 200

@wishlist_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
@profile_route
def remove_from_wishlist(item_id):
    """
    Remove an item from the user's wishlist (customer only).

    :param item_id: ID of the wishlist item to remove.
    :return: A JSON response with a success message, or an error message if the item is not in the wishlist.
    """
    auth_error = authorize_customer()
    if auth_error:
        return auth_error

    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    # Find the wishlist entry
    wishlist_entry = Wishlist.query.filter_by(user_id=user.id, item_id=item_id).first()
    if not wishlist_entry:
        return jsonify({"error": "Item not in wishlist"}), 404

    db.session.delete(wishlist_entry)
    db.session.commit()

    return jsonify({"message": "Item removed from wishlist"}), 200
