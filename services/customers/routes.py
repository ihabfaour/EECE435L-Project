from flask import Blueprint, request, jsonify
from .models import Customer
from database.db_config import db
import bcrypt

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/register', methods=['POST'])
def register_customer():
    try:
        data = request.json
        # Check if username exists
        if Customer.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        new_customer = Customer(
            full_name=data['full_name'],
            username=data['username'],
            password=hashed_password.decode('utf-8'),
            age=data['age'],
            address=data['address'],
            gender=data['gender'],
            marital_status=data['marital_status']
        )

        db.session.add(new_customer)
        db.session.commit()

        return jsonify({"message": "Customer registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        # Query the customer by ID
        customer = Customer.query.get(customer_id)

        # If the customer doesn't exist, return an error
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Delete the customer from the database
        db.session.delete(customer)
        db.session.commit()

        return jsonify({"message": f"Customer with ID {customer_id} deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
