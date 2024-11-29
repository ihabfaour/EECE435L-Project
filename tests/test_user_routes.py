import pytest
from app import app, db
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
            print(app.url_map)  # Add this line to debug registered routes

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
            username="johndoe",
            password="hashedpassword",
            age=25,
            address="123 Test St",
            gender="Male",
            marital_status="Single",
            role="customer",
            wallet_balance=100.0
        )
        db.session.add(test_user)
        db.session.commit()

        # Generate JWT token
        token = create_access_token(identity="johndoe")
    return {"Authorization": f"Bearer {token}"}


def test_register_user(client):
    """Test the user registration route."""
    response = client.post('/user/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword123",
        "age": 30,
        "address": "123 Main Street",
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 201
    assert b"User registered successfully" in response.data


def test_register_duplicate_user(client):
    """Test registration with a duplicate username."""
    client.post('/user/register', json={
        "full_name": "Jane Doe",
        "username": "janedoe",
        "password": "password123",
        "age": 28,
        "address": "456 Elm Street",
        "gender": "Female",
        "marital_status": "Married"
    })
    response = client.post('/user/register', json={
        "full_name": "Jane Smith",
        "username": "janedoe",
        "password": "differentpassword123",
        "age": 25,
        "address": "789 Oak Avenue",
        "gender": "Female",
        "marital_status": "Single"
    })
    assert response.status_code == 400
    assert b"Username already exists" in response.data


def test_login_user(client):
    """Test the user login route."""
    client.post('/user/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword123",
        "age": 30,
        "address": "123 Main Street",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = client.post('/user/login', json={
        "username": "johndoe",
        "password": "securepassword123"
    })
    assert response.status_code == 200
    assert b"Login successful" in response.data


def test_login_invalid_user(client):
    """Test login with invalid credentials."""
    response = client.post('/user/login', json={
        "username": "invaliduser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_get_all_users(client, auth_headers):
    """Test fetching all users (requires admin access)."""
    # Add some users
    client.post('/user/register', json={
        "full_name": "User One",
        "username": "userone",
        "password": "password1",
        "age": 25,
        "address": "123 First Street",
        "gender": "Male",
        "marital_status": "Single"
    })
    client.post('/user/register', json={
        "full_name": "User Two",
        "username": "usertwo",
        "password": "password2",
        "age": 30,
        "address": "456 Second Avenue",
        "gender": "Female",
        "marital_status": "Married"
    })
    response = client.get('/user/', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json) == 3  # Includes testuser


def test_get_user_by_id(client, auth_headers):
    """Test fetching a user by ID."""
    client.post('/user/register', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "securepassword123",
        "age": 30,
        "address": "123 Main Street",
        "gender": "Male",
        "marital_status": "Single"
    })
    response = client.get('/user/1', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['username'] == "johndoe"

def test_delete_user(client, auth_headers):
    """Test deleting the logged-in user."""
    response = client.delete('/user/delete', headers=auth_headers)
    assert response.status_code == 200
    assert b"deleted successfully" in response.data

    # Verify the user no longer exists
    response = client.get('/user/1', headers=auth_headers)
    assert response.status_code == 404
    assert b"Customer not found" in response.data


def test_update_user(client, auth_headers):
    """Test updating user information."""
    response = client.patch('/user/update', json={
        "full_name": "Updated User",
        "age": 26
    }, headers=auth_headers)
    assert response.status_code == 200
    assert b"Customer updated successfully" in response.data

    # Verify the update
    response = client.get('/user/1', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['full_name'] == "Updated User"
    assert response.json['age'] == 26


def test_charge_wallet(client, auth_headers):
    """Test charging the wallet of the logged-in user."""
    response = client.post('/user/wallet/charge', json={"amount": 50}, headers=auth_headers)
    assert response.status_code == 200
    assert b"successfully added to wallet" in response.data


def test_deduct_wallet(client, auth_headers):
    """Test deducting funds from the wallet of the logged-in user."""
    response = client.post('/user/wallet/deduct', json={"amount": 30}, headers=auth_headers)
    assert response.status_code == 200
    assert b"successfully deducted from wallet" in response.data

