import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "http://localhost:3000"

@pytest.fixture
def admin_driver():
    # 1. Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 10)
    
    # 2. Perform Admin Login (Pre-condition for UC-7)
    # Wait up to 10 seconds for the email field to appear on the screen
    email_field = wait.until(EC.visibility_of_element_located((By.ID, "email")))
    email_field.send_keys("your_email_here") # Replace with actual admin email
    password_field = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    password_field.send_keys("your_password_here") # Replace with actual admin password

    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOGIN')]")))
    login_btn.click()
    
    yield driver # This passes the logged-in browser to test functions
    
    # 3. Teardown
    driver.quit()


def test_tp_09_009_empty_database_state(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # ==========================================
    # PART 1: BLOCK AUTO-POPULATION API
    # ==========================================
    # Instruct Chrome to block the specific auto-fetch endpoint so the DB stays empty
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["*fetch-and-store*"]})
    
    # Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    time.sleep(2)
    
    # Wait for the data fetching to resolve (the blocked request will just quietly fail in the background)
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass
        
    # ==========================================
    # PART 2: VERIFY EMPTY STATE IS RENDERED
    # ==========================================
    
    # First, verify that the table did NOT render (ensuring our empty DB precondition is met)
    table_exists = driver.find_elements(By.XPATH, "//table//tbody")
    if table_exists:
        # Re-enable all URLs before failing just in case
        driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": []})
        pytest.fail("Precondition Failed: The database is not empty. Please manually delete all records before running this test.")

    # Look for the empty state container
    try:
        empty_state_container = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'text-center py-12')]")))
    except Exception:
        driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": []})
        pytest.fail("Test Failed: The empty state UI container did not render on the page.")

    # ==========================================
    # PART 3: STRICT SRS TEXT ASSERTION
    # ==========================================
    
    actual_ui_text = empty_state_container.text
    expected_srs_text = "No data available"
    
    # Restore network functionality for future tests
    driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": []})
    
    # This assertion will fail because the React UI displays "No Weather Data" instead of "No data available"
    assert expected_srs_text in actual_ui_text, \
        f"DEFECT FOUND: SRS (TC-09-009) explicitly requires the message '{expected_srs_text}'. Instead, the system displayed:\n'{actual_ui_text}'"