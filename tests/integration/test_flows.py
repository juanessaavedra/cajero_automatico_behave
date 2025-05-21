# tests/integration/test_flows.py
import pytest
from app import app, USUARIO

@pytest.fixture
def client():
    """Configura un cliente de prueba para la aplicación Flask"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test_key'
    
    with app.test_client() as client:
        with app.app_context():
            # Reiniciar datos de usuario para cada prueba
            USUARIO["saldo"] = 700000
            USUARIO["contraseña"] = "12345"
        yield client

def test_flujo_deposito_retiro(client):
    """
    Prueba de integración que simula un flujo completo:
    1. Iniciar sesión
    2. Realizar un depósito
    3. Verificar saldo actualizado
    4. Realizar un retiro
    5. Verificar saldo final
    """
    # Paso 1: Iniciar sesión
    response = client.post('/login', data={'password': '12345'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'CAJERO ELECTR\xc3\x93NICO' in response.data
    
    saldo_inicial = USUARIO["saldo"]
    
    # Paso 2: Realizar un depósito
    monto_deposito = 150000
    response = client.post('/depositar', data={'monto': monto_deposito}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dep\xc3\xb3sito exitoso' in response.data
    
    # Paso 3: Verificar saldo actualizado (navegando a consulta)
    response = client.get('/consultar')
    assert response.status_code == 200
    nuevo_saldo = saldo_inicial + monto_deposito
    assert str(nuevo_saldo).encode() in response.data or f"{nuevo_saldo:,.2f}".encode() in response.data
    
    # Paso 4: Realizar un retiro
    monto_retiro = 50000
    response = client.post('/retirar', data={'monto': monto_retiro}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Retiro exitoso' in response.data
    
    # Paso 5: Verificar saldo final
    response = client.get('/consultar')
    assert response.status_code == 200
    saldo_final = nuevo_saldo - monto_retiro
    assert str(saldo_final).encode() in response.data or f"{saldo_final:,.2f}".encode() in response.data
    assert USUARIO["saldo"] == saldo_final

def test_flujo_cambio_password_y_reinicio_sesion(client):
    """
    Prueba de integración que simula:
    1. Iniciar sesión
    2. Cambiar contraseña
    3. Cerrar sesión
    4. Iniciar sesión con la nueva contraseña
    5. Realizar una operación adicional (consulta de saldo)
    """
    # Paso 1: Iniciar sesión
    response = client.post('/login', data={'password': '12345'}, follow_redirects=True)
    assert response.status_code == 200
    
    # Paso 2: Cambiar contraseña
    nueva_password = '67890'
    response = client.post('/cambiar_password', data={
        'password_actual': '12345',
        'password_nueva': nueva_password,
        'password_confirm': nueva_password
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'exitosamente' in response.data
    
    # Paso 3: Cerrar sesión
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Bienvenido al banco de Temu' in response.data
    
    # Paso 4: Iniciar sesión con nueva contraseña
    response = client.post('/login', data={'password': nueva_password}, follow_redirects=True)
    assert response.status_code == 200
    assert b'CAJERO ELECTR\xc3\x93NICO' in response.data
    
    # Paso 5: Realizar consulta para confirmar que la sesión está activa
    response = client.get('/consultar')
    assert response.status_code == 200
    assert b'Su saldo actual es:' in response.data

def test_flujo_completo_multiples_operaciones(client):
    """
    Prueba de integración compleja que simula:
    1. Iniciar sesión
    2. Consultar saldo inicial
    3. Realizar un depósito
    4. Realizar un retiro
    5. Cambiar contraseña
    6. Cerrar sesión
    7. Iniciar sesión con nueva contraseña
    8. Consultar saldo final
    """
    # Paso 1: Iniciar sesión
    client.post('/login', data={'password': '12345'}, follow_redirects=True)
    
    # Paso 2: Consultar saldo inicial
    response = client.get('/consultar')
    saldo_inicial = USUARIO["saldo"]
    
    # Paso 3: Realizar un depósito
    monto_deposito = 200000
    client.post('/depositar', data={'monto': monto_deposito}, follow_redirects=True)
    saldo_despues_deposito = saldo_inicial + monto_deposito
    
    # Paso 4: Realizar un retiro
    monto_retiro = 100000
    client.post('/retirar', data={'monto': monto_retiro}, follow_redirects=True)
    saldo_despues_retiro = saldo_despues_deposito - monto_retiro
    
    # Paso 5: Cambiar contraseña
    nueva_password = 'abcde'
    client.post('/cambiar_password', data={
        'password_actual': '12345',
        'password_nueva': nueva_password,
        'password_confirm': nueva_password
    }, follow_redirects=True)
    
    # Paso 6: Cerrar sesión
    client.get('/logout')
    
    # Paso 7: Iniciar sesión con nueva contraseña
    client.post('/login', data={'password': nueva_password}, follow_redirects=True)
    
    # Paso 8: Consultar saldo final
    response = client.get('/consultar')
    assert response.status_code == 200
    
    # Verificación final: el saldo debe ser igual al calculado después de todas las operaciones
    assert USUARIO["saldo"] == saldo_despues_retiro