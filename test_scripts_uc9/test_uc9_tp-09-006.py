import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

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


def test_tp_09_006_invalid_dataset_format(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    time.sleep(2)
    
    # ==========================================
    # PART 1: CREATE & UPLOAD INVALID FILE
    # ==========================================
    
    # Create a dummy invalid text file on the fly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    invalid_file_path = os.path.join(current_dir, "weather_report.txt")
    
    with open(invalid_file_path, 'w') as f:
        f.write("This is an invalid file format test.")
        
    try:
        # Locate the file input and send the invalid file path
        file_input = wait.until(EC.presence_of_element_located((By.ID, "csvFile")))
        file_input.send_keys(invalid_file_path)
        
        time.sleep(1) # Allow React state to update
        
        # Click the "Upload CSV" button
        upload_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Upload CSV')]")))
        upload_btn.click()
        
        # ==========================================
        # PART 2: VERIFY ERROR MESSAGE
        # ==========================================
        
        # Wait for the red error alert to appear
        error_alert = wait.until(EC.visibility_of_element_located((
            By.XPATH, "//div[contains(@class, 'text-red-800')]"
        )))
        
        assert error_alert.is_displayed(), "Test Failed: System did not display an error message when an invalid file was uploaded."
        
    finally:
        # Clean up the dummy file after the test
        if os.path.exists(invalid_file_path):
            os.remove(invalid_file_path)