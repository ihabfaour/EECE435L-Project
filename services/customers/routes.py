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

@customers_bp.route('/<int:customer_id>', methods=['PATCH'])
def update_customer(customer_id):
    try:
        # Get the customer by ID
        customer = Customer.query.get(customer_id)

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Update fields from JSON payload
        data = request.json
        if "full_name" in data:
            customer.full_name = data["full_name"]
        if "username" in data:
            customer.username = data["username"]
        if "password" in data:
            hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())
            customer.password = hashed_password.decode('utf-8')
        if "age" in data:
            customer.age = data["age"]
        if "address" in data:
            customer.address = data["address"]
        if "gender" in data:
            customer.gender = data["gender"]
        if "marital_status" in data:
            customer.marital_status = data["marital_status"]
        if "wallet_balance" in data:
            customer.wallet_balance = data["wallet_balance"]

        # Save changes
        db.session.commit()
        return jsonify({"message": "Customer updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@customers_bp.route('/', methods=['GET'])
def get_all_customers():
    try:
        # Query all customers
        customers = Customer.query.all()

        # Serialize the result
        result = [
            {
                "id": customer.id,
                "full_name": customer.full_name,
                "username": customer.username,
                "age": customer.age,
                "address": customer.address,
                "gender": customer.gender,
                "marital_status": customer.marital_status,
                "wallet_balance": float(customer.wallet_balance),
            }
            for customer in customers
        ]

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    try:
        # Query the customer by ID
        customer = Customer.query.get(customer_id)

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Serialize the result
        result = {
            "id": customer.id,
            "full_name": customer.full_name,
            "username": customer.username,
            "age": customer.age,
            "address": customer.address,
            "gender": customer.gender,
            "marital_status": customer.marital_status,
            "wallet_balance": float(customer.wallet_balance),
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@customers_bp.route('/<int:customer_id>/charge', methods=['POST'])
def charge_wallet(customer_id):
    try:
        # Get the customer by ID
        customer = Customer.query.get(customer_id)

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Get the amount to charge from the request
        data = request.json
        amount = data.get("amount")

        if not amount or amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        # Update wallet balance
        customer.wallet_balance += amount
        db.session.commit()

        return jsonify({"message": f"${amount} successfully added to wallet", 
                        "wallet_balance": float(customer.wallet_balance)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@customers_bp.route('/<int:customer_id>/deduct', methods=['POST'])
def deduct_wallet(customer_id):
    try:
        # Get the customer by ID
        customer = Customer.query.get(customer_id)

        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        # Get the amount to deduct from the request
        data = request.json
        amount = data.get("amount")

        if not amount or amount <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        if customer.wallet_balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400

        # Deduct amount from wallet balance
        customer.wallet_balance -= amount
        db.session.commit()

        return jsonify({"message": f"${amount} successfully deducted from wallet", 
                        "wallet_balance": float(customer.wallet_balance)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
