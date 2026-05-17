import os
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


def test_tp_09_002_upload_valid_weather_data_csv(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    
    time.sleep(2)
    
    # Wait for loading to finish
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass

    # ==========================================
    # PART 1: UPLOAD CSV FILE
    # ==========================================
    
    # Ensure you have 'valid_weather_data.csv' in the exact same folder as your test script
    # This gets the absolute path which Selenium requires for file uploads
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, "valid_weather_data.csv")
    
    if not os.path.exists(csv_file_path):
        pytest.fail(f"Test Failed: The file was not found at {csv_file_path}")
        
    # Send the absolute file path directly to the <input type="file"> element. 
    # Do NOT click it first.
    file_input = driver.find_element(By.ID, "csvFile")
    file_input.send_keys(csv_file_path)
    
    # Give React a fraction of a second to update the state (csvFile) and enable the button
    time.sleep(1)
    
    # Now wait for the "Upload CSV" button to become clickable and click it
    upload_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload CSV')]")))
    upload_btn.click()
    
    # ==========================================
    # PART 2: VERIFY SUCCESS MESSAGE
    # ==========================================
    
    # Verify the system accepts and parses the file (Success Alert Banner)
    try:
        success_alert = wait.until(EC.visibility_of_element_located((
            By.XPATH, "//div[contains(@class, 'text-green-800') and contains(text(), 'successfully')]"
        )))
        assert success_alert.is_displayed(), "Test Failed: Success banner was not displayed after CSV upload."
    except Exception:
        pytest.fail("Test Failed: Timeout waiting for the upload success banner.")
        
    # ==========================================
    # PART 3: VERIFY RECORDS IN TABLE
    # ==========================================
    
    time.sleep(2) # Give React a moment to refetch and re-render the table with new data
    
    # Verify that the new data is populated in the table
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    record_found = any("2026" in row.text for row in rows)
    
    assert record_found is True, "Test Failed: The newly uploaded CSV records are not displaying in the table."