import pytest
from app.models import Usuario # Import only the model class, no db object

def test_usuario_instantiation():
    # Create an instance of the Usuario model
    user = Usuario(username="testuser", password="secure_password", saldo=1000.50)

    # Assert that the attributes are set correctly
    assert user.username == "testuser"
    assert user.password == "secure_password"
    assert user.saldo == 1000.50
    assert user.id is None # ID should be None before being saved to DB
    assert user.transacciones == [] # Relationship should be empty initially

def test_usuario_default_saldo():
    # Create an instance without specifying saldo
    user = Usuario(username="anotheruser", password="another_password")

    # Assert that the default saldo is applied
    assert user.username == "anotheruser"
    assert user.password == "another_password"
    assert user.saldo == 0.0 # This verifies the default set in your model definition
    assert user.id is None
    assert user.transacciones == []