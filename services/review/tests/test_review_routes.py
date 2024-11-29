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
#             VALUES ('Smartphone', 'Electronics', 800.0, 15);
#         """)
#         db.session.commit()
#         yield testing_client
#         db.session.remove()
#         db.drop_all()

# def test_submit_review(test_client):
#     review_data = {
#         "product_id": 1,
#         "rating": 5,
#         "comment": "Amazing product!"
#     }
#     response = test_client.post('/reviews/submit', data=json.dumps(review_data), content_type='application/json')
#     assert response.status_code == 201
#     data = json.loads(response.get_data(as_text=True))
#     assert data["review"]["rating"] == 5

# def test_get_product_reviews(test_client):
#     response = test_client.get('/reviews/product/1')
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert len(data) > 0

# def test_get_customer_reviews(test_client):
#     response = test_client.get('/reviews/customer', headers={"Authorization": "Bearer valid_test_token"})
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert len(data) > 0

# def test_update_review(test_client):
#     update_data = {
#         "rating": 4,
#         "comment": "Good product"
#     }
#     response = test_client.patch('/reviews/update/1', data=json.dumps(update_data), content_type='application/json')
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert data["review"]["rating"] == 4

# def test_delete_review(test_client):
#     response = test_client.delete('/reviews/delete/1', headers={"Authorization": "Bearer valid_test_token"})
#     assert response.status_code == 200
#     data = json.loads(response.get_data(as_text=True))
#     assert data["message"] == "Review deleted successfully"
