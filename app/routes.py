from flask import render_template, request, redirect, url_for, session, flash
from app.models import Usuario, Transaccion
from app import db

def register_routes(app):
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('menu'))
        return render_template('login.html')

    @app.route('/login', methods=['POST'])
    def login():
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(password=password).first()
        
        if usuario:
            session['user_id'] = usuario.id
            return redirect(url_for('menu'))
        else:
            flash('Contraseña incorrecta', 'error')
            return redirect(url_for('index'))

    @app.route('/menu')
    def menu():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        usuario = Usuario.query.get(session['user_id'])
        return render_template('menu.html', saldo=usuario.saldo)

    @app.route('/consultar')
    def consultar():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        usuario = Usuario.query.get(session['user_id'])
        return render_template('consulta.html', saldo=usuario.saldo)

    @app.route('/retirar', methods=['GET', 'POST'])
    def retirar():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        usuario = Usuario.query.get(session['user_id'])
        
        if request.method == 'POST':
            try:
                monto = float(request.form.get('monto'))
                if monto <= 0:
                    flash('El monto debe ser mayor que cero', 'error')
                elif monto > usuario.saldo:
                    flash('Fondos insuficientes para realizar el retiro', 'error')
                else:
                    usuario.saldo -= monto
                    db.session.commit()
                    flash(f'Retiro exitoso. Ha retirado: ${monto:,.2f}', 'success')
                    return redirect(url_for('menu'))
            except ValueError:
                flash('Ingrese un valor numérico válido', 'error')
        
        return render_template('retirar.html', saldo=usuario.saldo)

    @app.route('/depositar', methods=['GET', 'POST'])
    def depositar():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        usuario = Usuario.query.get(session['user_id'])
        
        if request.method == 'POST':
            try:
                monto = float(request.form.get('monto'))
                if monto <= 0:
                    flash('El monto debe ser mayor que cero', 'error')
                else:
                    usuario.saldo += monto
                    db.session.commit()
                    flash(f'Depósito exitoso. Ha depositado: ${monto:,.2f}', 'success')
                    return redirect(url_for('menu'))
            except ValueError:
                flash('Ingrese un valor numérico válido', 'error')
        
        return render_template('depositar.html')

    @app.route('/cambiar_password', methods=['GET', 'POST'])
    def cambiar_password():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        usuario = Usuario.query.get(session['user_id'])
        
        if request.method == 'POST':
            password_actual = request.form.get('password_actual')
            password_nueva = request.form.get('password_nueva')
            password_confirm = request.form.get('password_confirm')
            
            if password_actual != usuario.password:
                flash('Contraseña actual incorrecta', 'error')
            elif len(password_nueva) < 4:
                flash('La contraseña debe tener al menos 4 caracteres', 'error')
            elif password_nueva != password_confirm:
                flash('Las contraseñas no coinciden', 'error')
            else:
                usuario.password = password_nueva
                db.session.commit()
                flash('¡Contraseña cambiada exitosamente!', 'success')
                return redirect(url_for('menu'))
        
        return render_template('cambiar_password.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))