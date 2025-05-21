from locust import HttpUser, task, between
import random

class ATMUser(HttpUser):
    wait_time = between(1, 3)  # Tiempo de espera entre tareas (1-3 segundos)
    
    def on_start(self):
        """Método ejecutado cuando un usuario virtual comienza."""
        # Iniciar sesión antes de comenzar las tareas
        self.client.post("/login", {"password": "12345"})
    
    @task(3)
    def check_balance(self):
        """Consultar saldo (mayor frecuencia)."""
        with self.client.get("/consultar", catch_response=True) as response:
            if "Su saldo actual es:" not in response.text:
                response.failure("No se pudo cargar la página de consulta de saldo")
    
    @task(2)
    def withdraw_money(self):
        """Realizar retiros (frecuencia media)."""
        # Montos aleatorios entre 10,000 y 50,000
        amount = random.randint(1, 5) * 10000
        with self.client.post("/retirar", {"monto": str(amount)}, catch_response=True, follow_redirects=True) as response:
            if "Retiro exitoso" not in response.text and "Fondos insuficientes" not in response.text:
                response.failure("La operación de retiro falló")
    
    @task(2)
    def deposit_money(self):
        """Realizar depósitos (frecuencia media)."""
        # Montos aleatorios entre 10,000 y 100,000
        amount = random.randint(1, 10) * 10000
        with self.client.post("/depositar", {"monto": str(amount)}, catch_response=True, follow_redirects=True) as response:
            if "Depósito exitoso" not in response.text:
                response.failure("La operación de depósito falló")
    
    @task(1)
    def change_password(self):
        """Cambiar contraseña (menor frecuencia)."""
        with self.client.post("/cambiar_password", {
            "password_actual": "12345",
            "password_nueva": "12345",  # Mantenemos la misma para simplificar
            "password_confirm": "12345"
        }, catch_response=True, follow_redirects=True) as response:
            if "Contraseña cambiada exitosamente" not in response.text and "Contraseña actual incorrecta" not in response.text:
                response.failure("El cambio de contraseña falló")
    
    @task(1)
    def logout_and_login(self):
        """Cerrar sesión y volver a iniciar (menor frecuencia)."""
        # Cerrar sesión
        self.client.get("/logout")
        # Iniciar sesión de nuevo
        with self.client.post("/login", {"password": "12345"}, catch_response=True, follow_redirects=True) as response:
            if "CAJERO" not in response.text:
                response.failure("No se pudo iniciar sesión")