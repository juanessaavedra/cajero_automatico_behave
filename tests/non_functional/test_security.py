import pytest
from app import create_app, db
from app.models import Usuario

@pytest.fixture
def client():
    """Fixture para crear un cliente de prueba con base de datos en memoria."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_key'
    
    with app.app_context():
        db.create_all()
        # Crear un usuario de prueba
        test_user = Usuario(username="testuser", password="12345", saldo=10000.0)
        db.session.add(test_user)
        db.session.commit()
        
        with app.test_client() as client:
            yield client
            
        db.session.remove()
        db.drop_all()

def test_protected_routes_without_login(client):
    """Verificar que las rutas protegidas redirigen al login cuando no hay sesión."""
    protected_routes = [
        '/menu',
        '/consultar',
        '/retirar',
        '/depositar',
        '/cambiar_password'
    ]
    
    for route in protected_routes:
        response = client.get(route)
        # Verificar que se redirige al login (código 302)
        assert response.status_code == 302
        # Verificar que la redirección es al index
        assert response.location == '/' or response.location.endswith('/index')

def test_sql_injection_prevention(client):
    """Prueba básica para verificar protección contra inyección SQL."""
    # Intentar login con payloads SQL comunes
    sql_payloads = [
        "' OR 1=1 --",
        "admin' --",
        "' OR '1'='1",
        "'; DROP TABLE usuario; --"
    ]
    
    for payload in sql_payloads:
        response = client.post('/login', data={'password': payload})
        # No debería lograr iniciar sesión
        assert response.status_code == 302
        # Verificar que no se redirige al menú (éxito de login)
        assert '/menu' not in response.location

def test_brute_force_simulation(client):
    """Simular un ataque de fuerza bruta básico."""
    # En un sistema real, deberías tener protección contra intentos repetidos
    # Aquí solo verificamos que 20 intentos no bloquean la aplicación
    
    for i in range(20):
        response = client.post('/login', data={'password': f'wrong{i}'})
        # La aplicación debe seguir respondiendo
        assert response.status_code == 302