import pytest
from app import app, db
from services.customers.models import User
from services.inventory.models import Inventory
from services.review.models import Review
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
    app.config['JWT_SECRET_KEY'] = 'testsecret'

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            # Create a test user, admin user, and inventory item
            test_user = User(
                full_name="Test User",
                username="testuser",
                password="hashedpassword",
                age=25,
                address="123 Test St",
                gender="Male",
                marital_status="Single",
                role="customer",
                wallet_balance=100.0
            )
            admin_user = User(
                full_name="Admin User",
                username="adminuser",
                password="hashedpassword",
                age=30,
                address="456 Admin Ave",
                gender="Female",
                marital_status="Single",
                role="admin"
            )
            test_item = Inventory(
                name="Test Product",
                category="Electronics",
                price_per_item=50.0,
                description="A great product",
                stock_count=10
            )
            db.session.add(test_user)
            db.session.add(admin_user)
            db.session.add(test_item)
            db.session.commit()

        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Fixture to create a test user and generate JWT token for authentication."""
    with app.app_context():
        token = create_access_token(identity="testuser")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_auth_headers(client):
    """Fixture to create an admin user and generate JWT token for authentication."""
    with app.app_context():
        token = create_access_token(identity="adminuser")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def create_review(client, auth_headers):
    """Fixture to create a test review for a product."""
    # Create a product in the inventory
    client.post('/inventory/add', json={
        "name": "Test Product",
        "category": "Test Category",
        "price_per_item": 50.0,
        "stock_count": 10
    }, headers=auth_headers)

    # Submit a review for the created product
    response = client.post('/reviews/submit', json={
        "product_id": 1,
        "rating": 5,
        "comment": "Great product!"
    }, headers=auth_headers)

    return response.json  # Return the created review

def test_submit_review(client, auth_headers):
    """Test submitting a review."""
    response = client.post('/reviews/submit', json={
        "product_id": 1,
        "rating": 5,
        "comment": "Amazing product!"
    }, headers=auth_headers)

    assert response.status_code == 201
    assert b"Review submitted successfully" in response.data

def test_submit_review_missing_fields(client, auth_headers):
    """Test submitting a review with missing fields."""
    response = client.post('/reviews/submit', json={
        "product_id": 1,
        "rating": 5
    }, headers=auth_headers)

    assert response.status_code == 400
    assert b"Missing required fields" in response.data

def test_update_review(client, auth_headers):
    """Test updating a review."""
    # Submit a review first
    client.post('/reviews/submit', json={
        "product_id": 1,
        "rating": 4,
        "comment": "Good product."
    }, headers=auth_headers)

    # Update the review
    response = client.patch('/reviews/update/1', json={
        "rating": 5,
        "comment": "Excellent product!"
    }, headers=auth_headers)

    assert response.status_code == 200
    assert b"Review updated successfully" in response.data

def test_delete_review(client, auth_headers):
    """Test deleting a review."""
    # Submit a review first
    client.post('/reviews/submit', json={
        "product_id": 1,
        "rating": 4,
        "comment": "Good product."
    }, headers=auth_headers)

    # Delete the review
    response = client.delete('/reviews/delete/1', headers=auth_headers)

    assert response.status_code == 200
    assert b"Review deleted successfully" in response.data

def test_get_product_reviews(client, create_review):
    """Test fetching reviews for a specific product."""
    product_id = create_review["review"]["product_id"]

    # Fetch the reviews for the product
    response = client.get(f'/reviews/product/{product_id}')
    assert response.status_code == 200

    reviews = response.get_json()
    assert isinstance(reviews, list)
    assert len(reviews) > 0
    assert reviews[0]["product_id"] == product_id

def test_get_customer_reviews(client, auth_headers):
    """Test fetching reviews submitted by the logged-in customer."""
    # Submit a review first
    client.post('/reviews/submit', json={
        "product_id": 1,
        "rating": 4,
        "comment": "Good product."
    }, headers=auth_headers)

    # Fetch the reviews
    response = client.get('/reviews/customer', headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["comment"] == "Good product."

def test_submit_review_invalid_product(client, auth_headers):
    """Test submitting a review for a non-existent product."""
    response = client.post('/reviews/submit', json={
        "product_id": 99,
        "rating": 5,
        "comment": "Great product!"
    }, headers=auth_headers)

    assert response.status_code == 404
    assert b"Product not found" in response.data

# New Tests for Moderation Features

def test_flag_review(client, admin_auth_headers, create_review):
    """Test flagging a review for moderation."""
    review_id = create_review["review"]["id"]

    # Flag the review
    response = client.post(f'/reviews/flag/{review_id}', headers=admin_auth_headers)
    assert response.status_code == 200
    assert b"Review has been flagged for moderation" in response.data

def test_approve_review(client, admin_auth_headers, create_review):
    """Test approving a flagged review."""
    review_id = create_review["review"]["id"]

    # Flag the review first
    client.post(f'/reviews/flag/{review_id}', headers=admin_auth_headers)

    # Approve the flagged review
    response = client.post(f'/reviews/approve/{review_id}', headers=admin_auth_headers)
    assert response.status_code == 200
    assert b"Review has been approved" in response.data

def test_flag_non_existent_review(client, admin_auth_headers):
    """Test flagging a non-existent review."""
    response = client.post('/reviews/flag/99', headers=admin_auth_headers)
    assert response.status_code == 404
    assert b"Review not found" in response.data

def test_approve_non_existent_review(client, admin_auth_headers):
    """Test approving a non-existent review."""
    response = client.post('/reviews/approve/99', headers=admin_auth_headers)
    assert response.status_code == 404
    assert b"Review not found" in response.data

def test_approve_unflagged_review(client, admin_auth_headers, create_review):
    """Test approving a review that has not been flagged."""
    review_id = create_review["review"]["id"]

    # Attempt to approve the unflagged review
    response = client.post(f'/reviews/approve/{review_id}', headers=admin_auth_headers)
    assert response.status_code == 400
    assert b"Only flagged reviews can be approved" in response.data
