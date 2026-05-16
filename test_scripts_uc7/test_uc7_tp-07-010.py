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
    password_field.send_keys("your_passsword_here") # Replace with actual admin password

    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'LOGIN')]")))
    login_btn.click()
    
    yield driver # This passes the logged-in browser to test functions
    
    # 3. Teardown
    driver.quit()


def test_tp_07_010_exception_user_list_fails(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # ==========================================
    # PART 1: SIMULATE CONNECTION FAILURE
    # ==========================================
    
    # Turn off network before navigating to simulate database/backend unreachable on module entry
    driver.set_network_conditions(
        offline=True,
        latency=5,
        download_throughput=500 * 1024,
        upload_throughput=500 * 1024
    )
    
    try:
        # 1. Navigate to User Management
        user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
        user_management_link.click()
        
        # ==========================================
        # PART 2: VERIFY ERROR HANDLING
        # ==========================================
        
        # Look for the fallback error message rendered by the UI instead of crashing
        error_msg = wait.until(EC.visibility_of_element_located((
            By.XPATH, "//div[contains(@class, 'text-red-600') and (contains(text(), 'Failed to fetch') or contains(text(), 'Unable to retrieve'))]"
        )))
        
        assert error_msg.is_displayed(), "Test Failed: Exception flow for data loading failure was not handled gracefully on the UI."
        
    finally:
        # Always restore network conditions
        driver.set_network_conditions(
            offline=False,
            latency=5,
            download_throughput=500 * 1024,
            upload_throughput=500 * 1024
        )