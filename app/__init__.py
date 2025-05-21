from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Inicialización del objeto db
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object('app.config.Config')
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Registrar rutas
    from app.routes import register_routes
    register_routes(app)
    
    # Crear base de datos
    with app.app_context():
        from app.models import Usuario, Transaccion
        db.create_all()
        
        # Crear usuario inicial si no existe
        from app.models import Usuario
        if not Usuario.query.filter_by(username="admin").first():
            usuario = Usuario(username="admin", password="12345", saldo=700000)
            db.session.add(usuario)
            db.session.commit()
    
    return app