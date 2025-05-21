from app import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    saldo = db.Column(db.Float, default=0.0)
    transacciones = db.relationship('Transaccion', backref='usuario', lazy=True)
    
    def __init__(self, username, password, saldo=0.0):
        self.username = username
        self.password = password
        self.saldo = saldo

class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # 'deposito' o 'retiro'
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)