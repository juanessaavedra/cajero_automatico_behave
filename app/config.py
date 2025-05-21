import os

class Config:
    # Clave secreta para las sesiones
    SECRET_KEY = os.urandom(24)
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cajero.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False