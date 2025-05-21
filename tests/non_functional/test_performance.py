import pytest
from app import create_app, db
from app.models import Usuario

@pytest.fixture(scope="module")
def app_with_db():
    """Fixture para crear una app Flask con base de datos en memoria."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_key'
    
    with app.app_context():
        db.create_all()
        # Añadir datos iniciales
        test_user = Usuario(username="testuser", password="12345", saldo=500000.0)
        db.session.add(test_user)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app_with_db):
    """Fixture para obtener un cliente de prueba."""
    with app_with_db.test_client() as client:
        # Iniciar sesión antes de las pruebas
        client.post('/login', data={'password': '12345'})
        yield client

def test_menu_page_load_performance(benchmark, client):
    """Medir rendimiento de carga de la página de menú."""
    # Usar benchmark para medir el rendimiento
    result = benchmark(client.get, '/menu')
    assert result.status_code == 200

def test_consultar_performance(benchmark, client):
    """Medir rendimiento de la consulta de saldo."""
    result = benchmark(client.get, '/consultar')
    assert result.status_code == 200

def test_retirar_performance(benchmark, client):
    """Medir rendimiento de la operación de retiro."""
    def retirar():
        return client.post('/retirar', data={'monto': '10000'}, follow_redirects=True)
    
    result = benchmark(retirar)
    assert result.status_code == 200