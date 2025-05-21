import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture
def setup():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get("http://127.0.0.1:5000")
    # Wait for the page to fully load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    yield driver
    driver.quit()

def test_login_success(setup):
    driver = setup
    # Wait explicitly for the password field to be visible
    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )
    password_field.send_keys("12345")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Verificar redirección exitosa al menú
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Consultar Saldo')]"))
    )
    assert "Saldo disponible:" in driver.page_source

def test_login_failure(setup):
    driver = setup
    # Wait explicitly for the password field to be visible
    password_field = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )
    password_field.send_keys("contraseña_incorrecta")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    
    # Verificar mensaje de error
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
    )
    assert "Contraseña incorrecta" in driver.page_source