import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app, db
from app.models import Usuario

# Fixture to set up the Flask application context for database operations
@pytest.fixture(scope='module')
def app_context():
    app = create_app()
    with app.app_context():
        # Ensure a clean database for tests
        db.drop_all()
        db.create_all()
        # Create a test user
        if not Usuario.query.filter_by(username="testuser").first():
            test_user = Usuario(username="testuser", password="12345", saldo=1000000.0)
            db.session.add(test_user)
            db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()  # Clean up database after tests in the module

# Fixture to run the Flask app for live testing
@pytest.fixture(scope='module')
def live_server(app_context):
    app = app_context
    from werkzeug.serving import run_simple
    import threading

    # Use a specific port for testing
    port = 5001
    hostname = '127.0.0.1'

    # Function to run the Flask app in a separate thread
    def run_app():
        run_simple(hostname, port, app, use_reloader=False, use_debugger=False)

    server_thread = threading.Thread(target=run_app)
    server_thread.daemon = True  # Allow main thread to exit even if server thread is running
    server_thread.start()

    # Wait for the server to start (you might need a more robust check here)
    WebDriverWait(app.test_client(), 10).until(
        lambda client: client.get('/').status_code == 200
    )

    yield f"http://{hostname}:{port}"

# Fixture for the Selenium WebDriver
@pytest.fixture
def browser(live_server):
    try:
        # This is the more modern way with Selenium 4.6+ and webdriver-manager 4.0+
        driver = webdriver.Chrome()
    except Exception:
        # Fallback for older setups or if direct setup fails
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)

    driver.get(live_server)  # Navigate to the live server URL
    driver.implicitly_wait(5)  # Set an implicit wait for elements

    yield driver
    driver.quit()

def test_login_success(browser):
    # The browser fixture already navigated to the base URL
    password_field = browser.find_element(By.NAME, "password")
    password_field.send_keys("12345")
    browser.find_element(By.XPATH, "//button[@type='submit']").click()

    # Verify successful redirection to the menu
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Consultar Saldo')]"))
    )
    assert "Saldo disponible:" in browser.page_source

def test_login_failure(browser):
    password_field = browser.find_element(By.NAME, "password")
    password_field.send_keys("wrong_password")
    browser.find_element(By.XPATH, "//button[@type='submit']").click()

    # Verify error message
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
    )
    assert "Contraseña incorrecta" in browser.page_source