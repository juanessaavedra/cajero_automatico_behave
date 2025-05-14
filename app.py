# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave para manejar sesiones

# Datos de usuario 
USUARIO = {
    "saldo": 700000,
    "contraseña": "12345"
}


@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('menu'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    password = request.form.get('password')
    
    if password == USUARIO["contraseña"]:
        session['logged_in'] = True
        return redirect(url_for('menu'))
    else:
        flash('Contraseña incorrecta', 'error')
        return redirect(url_for('index'))


@app.route('/menu')
def menu():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    return render_template('menu.html', saldo=USUARIO["saldo"])


@app.route('/consultar')
def consultar():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    return render_template('consulta.html', saldo=USUARIO["saldo"])


@app.route('/retirar', methods=['GET', 'POST'])
def retirar():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            monto = float(request.form.get('monto'))
            if monto <= 0:
                flash('El monto debe ser mayor que cero', 'error')
            elif monto > USUARIO["saldo"]:
                flash('Fondos insuficientes para realizar el retiro', 'error')
            else:
                USUARIO["saldo"] -= monto
                flash(f'Retiro exitoso. Ha retirado: ${monto:,.2f}', 'success')
                return redirect(url_for('menu'))
        except ValueError:
            flash('Ingrese un valor numérico válido', 'error')
    
    return render_template('retirar.html', saldo=USUARIO["saldo"])


@app.route('/depositar', methods=['GET', 'POST'])
def depositar():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            monto = float(request.form.get('monto'))
            if monto <= 0:
                flash('El monto debe ser mayor que cero', 'error')
            else:
                USUARIO["saldo"] += monto
                flash(f'Depósito exitoso. Ha depositado: ${monto:,.2f}', 'success')
                return redirect(url_for('menu'))
        except ValueError:
            flash('Ingrese un valor numérico válido', 'error')
    
    return render_template('depositar.html')


@app.route('/cambiar_password', methods=['GET', 'POST'])
def cambiar_password():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        password_actual = request.form.get('password_actual')
        password_nueva = request.form.get('password_nueva')
        password_confirm = request.form.get('password_confirm')
        
        if password_actual != USUARIO["contraseña"]:
            flash('Contraseña actual incorrecta', 'error')
        elif len(password_nueva) < 4:
            flash('La contraseña debe tener al menos 4 caracteres', 'error')
        elif password_nueva != password_confirm:
            flash('Las contraseñas no coinciden', 'error')
        else:
            USUARIO["contraseña"] = password_nueva
            flash('¡Contraseña cambiada exitosamente!', 'success')
            return redirect(url_for('menu'))
    
    return render_template('cambiar_password.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)