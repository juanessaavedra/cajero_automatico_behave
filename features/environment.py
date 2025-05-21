from app import create_app, db
from app.models import Usuario

def before_all(context):
    """Configuración inicial antes de todas las pruebas"""
    # Configurar la aplicación con una base de datos en memoria
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    context.app = app
    context.client = app.test_client()
    
    # Crear tablas
    with app.app_context():
        db.create_all()

def before_scenario(context, scenario):
    """Se ejecuta antes de cada escenario"""
    with context.app.app_context():
        # Limpiar y reiniciar la base de datos para cada escenario
        db.session.query(Usuario).delete()
        db.session.commit()
        
        # Crear usuario de prueba con saldo predeterminado
        test_user = Usuario(username="testuser", password="12345", saldo=700000.0)
        db.session.add(test_user)
        db.session.commit()
    
    # Limpiar la sesión web
    with context.client.session_transaction() as sess:
        if 'user_id' in sess:
            del sess['user_id']

def after_scenario(context, scenario):
    """Limpieza después de cada escenario"""
    # Limpiamos la sesión explícitamente
    context.client.get('/logout')

def after_all(context):
    """Se ejecuta después de todas las pruebas"""
    # Limpiar la base de datos
    with context.app.app_context():
        db.drop_all()