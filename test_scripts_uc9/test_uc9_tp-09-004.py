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


def test_tp_09_004_update_specific_weather_records(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    
    time.sleep(2)
    
    # Wait for initial loading to finish
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass

    # ==========================================
    # PART 1: OPEN EDIT MODAL
    # ==========================================
    
    # Locate the first row in the table and click its Edit button (the first button in the actions column)
    edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//table//tbody//tr[1]//button[1]")))
    edit_button.click()
    
    # Wait for the Edit Weather Record modal to appear
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Edit Weather Record')]")))
    
    # ==========================================
    # PART 2: UPDATE TEMPERATURE
    # ==========================================
    
    # Locate the temperature input inside the modal (using the specific modal ID)
    temp_input = wait.until(EC.visibility_of_element_located((By.ID, "modal-temperature")))
    
    # Clear the existing value and input the new target value (34)
    temp_input.clear()
    temp_input.send_keys("34")
    
    # Click the "Update Record" button inside the modal
    # We use a specific XPath to ensure we click the button inside the modal overlay, not the background one
    update_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed')]//button[contains(., 'Update Record')]")
    update_btn.click()
    
    # ==========================================
    # PART 3: VERIFY SUCCESS
    # ==========================================
    
    # Verify the system displays the success banner
    try:
        success_alert = wait.until(EC.visibility_of_element_located((
            By.XPATH, "//div[contains(@class, 'text-green-800') and contains(text(), 'successfully')]"
        )))
        assert success_alert.is_displayed(), "Test Failed: Success banner was not displayed after updating the record."
    except Exception:
        pytest.fail("Test Failed: Timeout waiting for the record update success banner.")
        
    # Wait for the modal to close completely
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Edit Weather Record')]")))
    
    time.sleep(2) # Allow React to refresh the table data
    
    # Verify the updated value is now reflected in the first row of the table
    first_row = driver.find_element(By.XPATH, "//table//tbody//tr[1]")
    
    assert "34°C" in first_row.text or "34" in first_row.text, "Test Failed: The updated temperature (34) is not displaying in the table row."