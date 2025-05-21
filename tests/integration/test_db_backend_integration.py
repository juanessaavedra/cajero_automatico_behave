import pytest
from app import create_app, db
from app.models import Usuario
from flask import session

# Fixture to set up a clean Flask application with an in-memory database for each test function
@pytest.fixture(scope='function')
def app_with_db_client():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use in-memory DB
    app.config['TESTING'] = True # Enable testing mode
    app.config['SECRET_KEY'] = 'test_secret_key_for_integration' # Fixed key for sessions

    with app.app_context():
        db.create_all() # Create tables for this in-memory DB
        # Optional: Add a known user to the DB for specific tests
        test_user = Usuario(username="integration_user", password="test_password", saldo=500000.0)
        db.session.add(test_user)
        db.session.commit()
        yield app.test_client() # Yield the test client
        db.session.remove() # Clean up session
        db.drop_all() # Drop tables after the test

def test_login_retrieves_user_from_db(app_with_db_client):
    client = app_with_db_client # The fixture yields the test client

    # Simulate a POST request to login with the known user's password
    response = client.post('/login', data={'password': 'test_password'}, follow_redirects=True)

    # Assert that login was successful (redirected to menu and session set)
    assert response.status_code == 200 # OK after redirect
    assert b'CAJERO ELECTR\xc3\x93NICO' in response.data # Verify presence of menu content

    with client.session_transaction() as sess:
        # Verify that the user_id is set in the session
        assert sess['user_id'] is not None
        # Optionally, verify the correct user ID from the database
        user_in_db = Usuario.query.filter_by(password="test_password").first()
        assert sess['user_id'] == user_in_db.id

    # Now, try to access a page that uses the database (e.g., menu or consultar)
    # The previous redirect already landed us on /menu, so check its content again
    assert b'Saldo disponible: $500,000.00' in response.data # Check displayed saldo