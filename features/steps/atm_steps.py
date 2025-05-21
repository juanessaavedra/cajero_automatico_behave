from behave import given, when, then
from flask import session
import re
from app.models import Usuario
from app import db

@given('I am on the ATM login screen')
def step_on_login_screen(context):
    """Navega a la pantalla de inicio"""
    response = context.client.get('/')
    context.response = response
    assert response.status_code == 200

@given('I have successfully logged in')
def step_logged_in(context):
    """Inicia sesión con credenciales válidas"""
    # Primero aseguramos que estamos en la página de login
    context.client.get('/')
    # Hacemos login con la contraseña del usuario de prueba
    response = context.client.post('/login', data={'password': '12345'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'CAJERO' in response.data

@given('I am on the main menu')
def step_on_main_menu(context):
    """Verifica que estamos en el menú principal"""
    response = context.client.get('/menu')
    context.response = response
    assert b'CAJERO' in response.data

@given('my current balance is "{balance}"')
def step_current_balance(context, balance):
    """Establece el saldo actual en la base de datos"""
    with context.app.app_context():
        # Extrae el número del formato de moneda
        amount = float(balance.replace('$', '').replace(',', ''))
        
        # Aseguramos que hay una sesión activa
        with context.client.session_transaction() as sess:
            user_id = sess.get('user_id')
            
            # Si hay una sesión activa, actualizamos el usuario correspondiente
            if user_id:
                user = Usuario.query.get(user_id)
                user.saldo = amount
                db.session.commit()
            else:
                # Si no hay sesión, actualizamos todos los usuarios de prueba
                users = Usuario.query.all()
                for user in users:
                    user.saldo = amount
                    db.session.commit()

@when('I enter the password "{password}"')
def step_enter_password(context, password):
    """Almacena la contraseña ingresada"""
    context.password = password

@when('I click the "{button}" button')
def step_click_button(context, button):
    """Simula hacer clic en un botón"""
    if button == "Login":
        response = context.client.post('/login', data={'password': context.password}, follow_redirects=True)
        context.response = response
    elif button == "Withdraw":
        response = context.client.post('/retirar', data={'monto': context.amount}, follow_redirects=True)
        context.response = response
    elif button == "Deposit":
        response = context.client.post('/depositar', data={'monto': context.amount}, follow_redirects=True)
        context.response = response
    elif button == "Change":
        response = context.client.post('/cambiar_password', data={
            'password_actual': context.current_password,
            'password_nueva': context.new_password,
            'password_confirm': context.confirm_password
        }, follow_redirects=True)
        context.response = response

@when('I select the "{option}" option')
def step_select_option(context, option):
    """Navega a una opción del menú"""
    option_map = {
        "Check Balance": "/consultar",
        "Withdraw Money": "/retirar",
        "Deposit Money": "/depositar",
        "Change Password": "/cambiar_password"
    }
    route = option_map.get(option, "/")
    response = context.client.get(route)
    context.response = response

@when('I enter the amount "{amount}"')
def step_enter_amount(context, amount):
    """Almacena el monto ingresado"""
    context.amount = amount

@when('I enter my current password "{password}"')
def step_enter_current_password(context, password):
    """Almacena la contraseña actual"""
    context.current_password = password

@when('I enter my new password "{password}"')
def step_enter_new_password(context, password):
    """Almacena la nueva contraseña"""
    context.new_password = password

@when('I confirm my new password "{password}"')
def step_confirm_new_password(context, password):
    """Almacena la confirmación de contraseña"""
    context.confirm_password = password

@then('I should see the main menu')
def step_should_see_main_menu(context):
    """Verifica que estamos en el menú principal"""
    response = context.client.get('/menu')
    assert b'CAJERO' in response.data
    assert response.status_code == 200

@then('I should see my available balance of "{balance}"')
def step_should_see_balance(context, balance):
    """Verifica que se muestra el saldo correcto"""
    response = context.client.get('/menu')
    # Busca el saldo en el HTML - puede variar el formato
    balance_text = balance.encode()
    # Considera posibles variaciones en el formato de la moneda
    simplified_balance = balance.replace(',', '').encode()
    assert (balance_text in response.data) or (simplified_balance in response.data)

@then('I should see the balance inquiry screen')
def step_should_see_balance_screen(context):
    """Verifica que estamos en la pantalla de consulta"""
    assert b'Consulta de Saldo' in context.response.data

@then('I should see the message "{message}"')
def step_should_see_message(context, message):
    """Verifica que se muestra un mensaje específico"""
    # Para mensajes flash, necesitamos seguir la redirección
    if hasattr(context, 'response') and context.response.status_code in [302, 303]:
        # Sigue la redirección
        context.response = context.client.get(context.response.location, follow_redirects=True)
    
    response_data = context.response.data
    
    # Para la consulta de saldo, verifica si es parte del contenido
    if message == "Su saldo actual es:":
        assert b"Su saldo actual es:" in response_data
    else:
        # Para mensajes flash, busca dentro de las alertas
        assert message.encode() in response_data

@then('I should have the option to "{option}"')
def step_should_have_option(context, option):
    """Verifica que existe una opción o enlace específico"""
    assert option.encode() in context.response.data

@then('my balance should be updated to "{balance}"')
def step_balance_should_be_updated(context, balance):
    """Verifica que el saldo se actualizó correctamente en la base de datos"""
    with context.app.app_context():
        # Convertir el saldo del formato de texto a número
        amount = float(balance.replace('$', '').replace(',', ''))
        
        # Obtener el ID del usuario de la sesión
        with context.client.session_transaction() as sess:
            user_id = sess.get('user_id')
            
        if user_id:
            # Verificar el saldo en la base de datos
            user = Usuario.query.get(user_id)
            assert abs(user.saldo - amount) < 0.01  # Permitir una pequeña diferencia por redondeo
        else:
            # Si no hay sesión, fallar la prueba
            assert False, "No hay usuario en sesión para verificar el saldo"

@then('I should return to the main menu')
def step_should_return_to_menu(context):
    """Verifica que regresamos al menú principal"""
    # Ya seguimos las redirecciones en los pasos anteriores
    assert b'CAJERO' in context.response.data

@then('my balance should remain at "{balance}"')
def step_balance_should_remain(context, balance):
    """Verifica que el saldo no cambió en la base de datos"""
    with context.app.app_context():
        # Convertir el saldo del formato de texto a número
        amount = float(balance.replace('$', '').replace(',', ''))
        
        # Obtener el ID del usuario de la sesión
        with context.client.session_transaction() as sess:
            user_id = sess.get('user_id')
            
        if user_id:
            # Verificar el saldo en la base de datos
            user = Usuario.query.get(user_id)
            assert abs(user.saldo - amount) < 0.01  # Permitir una pequeña diferencia por redondeo
        else:
            # Si no hay sesión, fallar la prueba
            assert False, "No hay usuario en sesión para verificar el saldo"

@then('I should stay on the withdrawal screen')
def step_should_stay_on_withdrawal(context):
    """Verifica que permanecemos en la pantalla de retiro"""
    assert b'Retirar Dinero' in context.response.data

@then('I should be able to log out')
def step_should_be_able_to_logout(context):
    """Verifica que podemos cerrar sesión"""
    # Cerrar sesión
    response = context.client.get('/logout')
    assert response.status_code in [302, 200]
    
    # Verificar que realmente nos desconectamos
    # Usar follow_redirects=True para seguir la redirección
    menu_response = context.client.get('/menu', follow_redirects=True)
    
    # Ahora deberíamos ver la página de login
    assert b'Ingrese' in menu_response.data or b'Login' in menu_response.data

@then('log in with the new password "{password}"')
def step_login_with_new_password(context, password):
    """Intenta iniciar sesión con la nueva contraseña"""
    # Primero, verificar que la contraseña se actualizó en la base de datos
    with context.app.app_context():
        # En este caso no podemos verificar directamente el password en la BD
        # porque no sabemos qué usuario específico estamos probando
        
        # Intentamos iniciar sesión con la nueva contraseña
        response = context.client.post('/login', data={'password': password}, follow_redirects=True)
        
        # Verificar que el login fue exitoso y estamos en el menú
        assert b'CAJERO' in response.data
        assert response.status_code == 200
        
        # Verificar que hay una sesión activa
        with context.client.session_transaction() as sess:
            assert 'user_id' in sess