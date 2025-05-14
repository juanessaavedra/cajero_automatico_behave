# features/environment.py

from app import app, USUARIO

def before_all(context):
    """Configuración inicial antes de todas las pruebas"""
    # Configura el cliente de pruebas de Flask
    context.app = app
    context.client = app.test_client()
    context.app.config['TESTING'] = True

def before_scenario(context, scenario):
    """Se ejecuta antes de cada escenario"""
    # Reinicia los datos del usuario para cada escenario
    USUARIO['saldo'] = 700000
    USUARIO['contraseña'] = '12345'
    
    # Limpia la sesión
    with context.app.test_request_context():
        context.client.get('/logout')

def after_all(context):
    """Se ejecuta después de todas las pruebas"""
    # No necesitamos hacer nada especial aquí
    pass