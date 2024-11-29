from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db_config import db
from .models import Review
from services.inventory.models import Inventory
from services.customers.models import User

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_review():
    """
    Submit a review for a product.

    :request json: {
        "product_id": int,  # ID of the product being reviewed
        "rating": int,      # Rating for the product (1-5)
        "comment": str      # Review comment
    }
    :return: JSON response containing the review details or an error message.
    """
    try:
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        product_id = data.get('product_id')
        rating = data.get('rating')
        comment = data.get('comment')

        # Validation
        if not product_id or not rating or not comment:
            return jsonify({"error": "Missing required fields"}), 400
        if not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be between 1 and 5"}), 400

        product = Inventory.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        review = Review(
            product_id=product_id,
            customer_username=current_user,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()

        return jsonify({"message": "Review submitted successfully", "review": review.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/update/<int:review_id>', methods=['PATCH'])
@jwt_required()
def update_review(review_id):
    """
    Update a review.

    :param review_id: ID of the review to update.
    :request json: {
        "rating": int,  # Updated rating (1-5)
        "comment": str  # Updated comment
    }
    :return: JSON response with the updated review details or an error message.
    """
    try:
        current_user = get_jwt_identity()
        review = Review.query.get(review_id)
        if not review or review.customer_username != current_user:
            return jsonify({"error": "Review not found or unauthorized"}), 404

        data = request.json
        if "rating" in data:
            if not (1 <= data["rating"] <= 5):
                return jsonify({"error": "Rating must be between 1 and 5"}), 400
            review.rating = data["rating"]
        if "comment" in data:
            review.comment = data["comment"]

        db.session.commit()
        return jsonify({"message": "Review updated successfully", "review": review.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/delete/<int:review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """
    Delete a review.

    :param review_id: ID of the review to delete.
    :return: JSON response indicating success or an error message.
    """
    try:
        current_user = get_jwt_identity()
        review = Review.query.get(review_id)
        if not review or review.customer_username != current_user:
            return jsonify({"error": "Review not found or unauthorized"}), 404

        db.session.delete(review)
        db.session.commit()
        return jsonify({"message": "Review deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_reviews(product_id):
    """
    Get all reviews for a specific product.

    :param product_id: ID of the product to fetch reviews for.
    :return: JSON response with a list of reviews or an error message.
    """
    try:
        reviews = Review.query.filter_by(product_id=product_id).all()
        result = [review.to_dict() for review in reviews]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reviews_bp.route('/customer', methods=['GET'])
@jwt_required()
def get_customer_reviews():
    """
    Get all reviews submitted by the currently logged-in customer.

    :return: JSON response with a list of reviews or an error message.
    """
    try:
        current_user = get_jwt_identity()
        reviews = Review.query.filter_by(customer_username=current_user).all()
        result = [review.to_dict() for review in reviews]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
