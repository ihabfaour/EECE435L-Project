# import pytest
# from flask import json
# from services.app import create_app
# from database.db_config import db

# @pytest.fixture(scope="module")
# def test_client():
#     app = create_app("testing")
#     testing_client = app.test_client()
#     with app.app_context():
#         db.create_all()
#         # Add test data
#         db.session.execute("""
#             INSERT INTO users (username, full_name, wallet_balance)
#             VALUES ('testuser', 'Test User', 1000.0);
#         """)
#         db.session.execute("""
#             INSERT INTO inventory (name, category, price_per_item, stock_count)
#             VALUES ('Laptop', 'Electronics', 1500.0, 10);
#         """)
#         db.session.commit()
#         yield testing_client
#         db.session.remove()
#         db.drop_all()

# def test_display_goods(test_client):
#     response = test_client.get('/sales/display')
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert isinstance(data, list)
#     assert len(data) > 0

# def test_get_good_details(test_client):
#     response = test_client.get('/sales/details/1')
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert data["name"] == "Laptop"

# def test_make_sale(test_client):
#     sale_data = {
#         "product_id": 1,
#         "quantity": 1
#     }
#     response = test_client.post('/sales/sale', data=json.dumps(sale_data), content_type='application/json')
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert data["sale_details"]["product_name"] == "Laptop"

# def test_get_purchase_history(test_client):
#     response = test_client.get('/sales/history', headers={"Authorization": "Bearer valid_test_token"})
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert len(data) > 0
