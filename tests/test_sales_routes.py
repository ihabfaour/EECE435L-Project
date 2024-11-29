import pytest
from app import app, db
from services.customers.models import User
from services.inventory.models import Inventory
from services.sales.models import Sale
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
            db.create_all()  # Initialize tables

        yield client

        with app.app_context():
            db.session.remove()
            db.drop_all()  # Clean up tables after tests

@pytest.fixture
def auth_headers(client):
    """Fixture to create a test user and generate JWT token for authentication."""
    with app.app_context():
        test_user = User(
            full_name="Test User",
            username="testuser",
            password="hashedpassword",
            age=25,
            address="123 Test St",
            gender="Male",
            marital_status="Single",
            role="customer",
            wallet_balance=200.0
        )
        db.session.add(test_user)
        db.session.commit()

        # Generate JWT token
        token = create_access_token(identity="testuser")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def setup_inventory():
    """Fixture to create test inventory items."""
    with app.app_context():
        item1 = Inventory(name="Item1", category="Category1", price_per_item=50, stock_count=10)
        item2 = Inventory(name="Item2", category="Category2", price_per_item=100, stock_count=5)
        db.session.add(item1)
        db.session.add(item2)
        db.session.commit()

# Test cases
def test_display_goods(client, setup_inventory):
    """Test the display of available goods."""
    response = client.get('/sales/display')
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['name'] == "Item1"

def test_get_good_details(client, setup_inventory):
    """Test retrieving details of a specific good."""
    response = client.get('/sales/details/1')
    assert response.status_code == 200
    assert response.json['name'] == "Item1"

    response = client.get('/sales/details/999')
    assert response.status_code == 404
    assert b"Item not found" in response.data

def test_make_sale(client, auth_headers, setup_inventory):
    """Test making a sale."""
    response = client.post('/sales/sale', json={"product_id": 1, "quantity": 2}, headers=auth_headers)
    assert response.status_code == 200
    assert b"Sale completed successfully" in response.data

    response = client.post('/sales/sale', json={"product_id": 1, "quantity": 20}, headers=auth_headers)
    assert response.status_code == 400
    assert b"Insufficient stock" in response.data

    response = client.post('/sales/sale', json={"product_id": 999, "quantity": 1}, headers=auth_headers)
    assert response.status_code == 404
    assert b"Product not found" in response.data

def test_get_purchase_history(client, auth_headers, setup_inventory):
    """Test retrieving purchase history of the customer."""
    # Make a sale to add to history
    client.post('/sales/sale', json={"product_id": 1, "quantity": 2}, headers=auth_headers)

    response = client.get('/sales/history', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['product_name'] == "Item1"
