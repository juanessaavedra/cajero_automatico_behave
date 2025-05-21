import pytest
from app import app, USUARIO

@pytest.fixture
def client():
    """Configura un cliente de prueba para la aplicación Flask"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test_key'  # Clave fija para pruebas
    
    with app.test_client() as client:
        with app.app_context():
            # Reiniciar datos de usuario para cada prueba
            USUARIO["saldo"] = 700000
            USUARIO["contraseña"] = "12345"
        yield client

def test_login_correcto(client):
    """Prueba que el login funcione correctamente con credenciales válidas"""
    # Primero cerramos sesión para asegurarnos que estamos en un estado limpio
    client.get('/logout')
    
    # Luego hacemos el login
    response = client.post('/login', data={
        'password': '12345'
    }, follow_redirects=True)
    
    # Verifica que la respuesta sea exitosa
    assert response.status_code == 200
    
    # Verificamos que estamos en la página de menú buscando texto específico de esa plantilla
    assert b'CAJERO ELECTR\xc3\x93NICO' in response.data
    assert b'Saldo disponible:' in response.data
    assert b'Retirar Dinero' in response.data

def test_retiro_exitoso(client):
    """Prueba que un retiro válido funcione correctamente"""
    # Primero iniciamos sesión
    client.post('/login', data={'password': '12345'})
    
    # Realizamos un retiro
    saldo_inicial = USUARIO["saldo"]
    monto_retiro = 50000
    
    response = client.post('/retirar', data={
        'monto': monto_retiro
    }, follow_redirects=True)
    
    # Verifica que el retiro fue exitoso y que el saldo se actualizó correctamente
    assert response.status_code == 200
    assert USUARIO["saldo"] == saldo_inicial - monto_retiro
    # Verificamos que hay un mensaje de éxito (esto aparecerá en el flash)
    assert b'Retiro exitoso' in response.data

def test_cambio_password(client):
    """Prueba que el cambio de contraseña funcione correctamente"""
    # Primero iniciamos sesión
    client.post('/login', data={'password': '12345'})
    
    # Luego cambiamos la contraseña
    response = client.post('/cambiar_password', data={
        'password_actual': '12345',
        'password_nueva': '67890',
        'password_confirm': '67890'
    }, follow_redirects=True)
    
    # Verifica que el cambio de contraseña fue exitoso
    assert response.status_code == 200
    assert USUARIO["contraseña"] == '67890'
    
    # Verificamos que hay un mensaje de éxito (esto aparecerá en el flash)
    assert b'exitosamente' in response.data
    
    # Verificamos que podemos iniciar sesión con la nueva contraseña
    client.get('/logout')  # Cerramos sesión primero
    
    response = client.post('/login', data={
        'password': '67890'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'CAJERO ELECTR\xc3\x93NICO' in response.data  # Texto que aparece en el menú