import pytest
from app import app, db
from services.inventory.models import Inventory
from services.customers.models import User
from flask_jwt_extended import create_access_token
import sys
import os

# Ensure the test suite can locate the app and services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def client():
    """Fixture to initialize the test client and database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ihab2003*@mysql-container/ecommerce_db'  # Replace with your test database details
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'testsecret'  # Set JWT secret key for testing

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()  # Initialize tables
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up tables after tests


@pytest.fixture
def admin_auth_headers(client):
    """Fixture to create an admin user and generate JWT token for authentication."""
    with app.app_context():
        admin_user = User(
            full_name="Admin User",
            username="admin",
            password="hashedpassword",
            age=35,
            address="456 Admin St",
            gender="Male",
            marital_status="Single",
            role="admin",
            wallet_balance=0.0
        )
        db.session.add(admin_user)
        db.session.commit()

        # Generate JWT token
        token = create_access_token(identity="admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_auth_headers(client):
    """Fixture to create a customer user and generate JWT token for authentication."""
    with app.app_context():
        customer_user = User(
            full_name="Customer User",
            username="customer",
            password="hashedpassword",
            age=30,
            address="123 Customer St",
            gender="Female",
            marital_status="Married",
            role="customer",
            wallet_balance=100.0
        )
        db.session.add(customer_user)
        db.session.commit()

        # Generate JWT token
        token = create_access_token(identity="customer")
    return {"Authorization": f"Bearer {token}"}


def test_add_inventory_item(client, admin_auth_headers):
    """Test adding an inventory item (admin only)."""
    response = client.post('/inventory/add', json={
        "name": "Laptop",
        "category": "electronics",
        "price_per_item": 1200.0,
        "description": "A high-end gaming laptop",
        "stock_count": 10
    }, headers=admin_auth_headers)
    assert response.status_code == 201
    assert b"Item added successfully" in response.data


def test_add_inventory_item_unauthorized(client, customer_auth_headers):
    """Test adding an inventory item (unauthorized access)."""
    response = client.post('/inventory/add', json={
        "name": "Laptop",
        "category": "electronics",
        "price_per_item": 1200.0,
        "description": "A high-end gaming laptop",
        "stock_count": 10
    }, headers=customer_auth_headers)
    assert response.status_code == 403
    assert b"Access forbidden" in response.data


def test_deduct_stock(client, admin_auth_headers):
    """Test deducting stock from an inventory item (admin only)."""
    # Add an item first
    client.post('/inventory/add', json={
        "name": "Phone",
        "category": "electronics",
        "price_per_item": 800.0,
        "description": "A smartphone",
        "stock_count": 20
    }, headers=admin_auth_headers)

    # Deduct stock
    response = client.post('/inventory/1/deduct', json={"quantity": 5}, headers=admin_auth_headers)
    assert response.status_code == 200
    assert b"5 units deducted" in response.data


def test_update_inventory_item(client, admin_auth_headers):
    """Test updating fields of an inventory item (admin only)."""
    # Add an item first
    client.post('/inventory/add', json={
        "name": "Tablet",
        "category": "electronics",
        "price_per_item": 500.0,
        "description": "A touchscreen tablet",
        "stock_count": 15
    }, headers=admin_auth_headers)

    # Update item
    response = client.patch('/inventory/1/update', json={"price_per_item": 550.0}, headers=admin_auth_headers)
    assert response.status_code == 200
    assert b"updated successfully" in response.data


def test_get_all_items(client, customer_auth_headers):
    """Test retrieving all items from inventory."""
    # Add some items
    with app.app_context():
        db.session.add(Inventory(name="Item1", category="electronics", price_per_item=100.0, description="Desc1", stock_count=5))
        db.session.add(Inventory(name="Item2", category="food", price_per_item=50.0, description="Desc2", stock_count=10))
        db.session.commit()

    response = client.get('/inventory/', headers=customer_auth_headers)
    assert response.status_code == 200
    assert len(response.json) == 2  # Two items added
