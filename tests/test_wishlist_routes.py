import pytest
from app import app, db
from services.wishlist.models import Wishlist
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


@pytest.fixture
def setup_inventory(client):
    """Fixture to add inventory items for testing."""
    with app.app_context():
        item1 = Inventory(name="Item1", category="electronics", price_per_item=100.0, description="Desc1", stock_count=5)
        item2 = Inventory(name="Item2", category="food", price_per_item=50.0, description="Desc2", stock_count=10)
        db.session.add(item1)
        db.session.add(item2)
        db.session.commit()


def test_add_to_wishlist(client, customer_auth_headers, setup_inventory):
    """Test adding an item to the wishlist."""
    response = client.post('/wishlist/add', json={"item_id": 1}, headers=customer_auth_headers)
    print(response.data)  # Debug the response data
    assert response.status_code == 201
    assert b"'Item1' has been added to your wishlist" in response.data


def test_add_to_wishlist_duplicate(client, customer_auth_headers, setup_inventory):
    """Test adding the same item to the wishlist multiple times."""
    client.post('/wishlist/add', json={"item_id": 1}, headers=customer_auth_headers)
    response = client.post('/wishlist/add', json={"item_id": 1}, headers=customer_auth_headers)
    assert response.status_code == 200
    assert b"'Item1' is already in your wishlist" in response.data


def test_view_wishlist(client, customer_auth_headers, setup_inventory):
    """Test viewing the wishlist."""
    # Add items to the wishlist
    client.post('/wishlist/add', json={"item_id": 1}, headers=customer_auth_headers)
    client.post('/wishlist/add', json={"item_id": 2}, headers=customer_auth_headers)

    response = client.get('/wishlist/', headers=customer_auth_headers)
    assert response.status_code == 200
    assert len(response.json) == 2  # Two items in wishlist


def test_remove_from_wishlist(client, customer_auth_headers, setup_inventory):
    """Test removing an item from the wishlist."""
    # Add an item to the wishlist
    client.post('/wishlist/add', json={"item_id": 1}, headers=customer_auth_headers)

    # Remove the item
    response = client.delete('/wishlist/1', headers=customer_auth_headers)
    assert response.status_code == 200
    assert b"Item removed from wishlist" in response.data


def test_remove_nonexistent_item(client, customer_auth_headers):
    """Test removing an item that is not in the wishlist."""
    response = client.delete('/wishlist/1', headers=customer_auth_headers)
    assert response.status_code == 404
    assert b"Item not in wishlist" in response.data


def test_add_to_wishlist_item_not_found(client, customer_auth_headers):
    """Test adding an item to the wishlist that does not exist in inventory."""
    response = client.post('/wishlist/add', json={"item_id": 999}, headers=customer_auth_headers)
    assert response.status_code == 404
    assert b"Item not found" in response.data
