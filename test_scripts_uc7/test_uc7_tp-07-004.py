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


def test_tp_07_004_update_user_status(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    target_user = "Jason"
    
    # ==========================================
    # PART 1: LOCATE AND CLICK VERIFY
    # ==========================================
    
    # Check if user is currently Pending, if so, click the Verify button inside their row
    try:
        verify_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//tr[contains(., '{target_user}') and contains(., 'Pending')]//button[@title='Verify User']"
        )))
        verify_btn.click()
    except Exception:
        pytest.fail(f"Test Failed: Could not find a 'Pending' status or 'Verify' button for user '{target_user}'. Make sure test data is properly seeded in the database.")
        
    # ==========================================
    # PART 2: VERIFY SYSTEM SAVES UPDATES
    # ==========================================
    
    # Wait for the network request to complete and the React state to update the UI
    time.sleep(2)
    
    # Check the row again to ensure the status icon/text has updated to "Verified"
    updated_row = driver.find_element(By.XPATH, f"//tr[contains(., '{target_user}')]")
    
    assert "Verified" in updated_row.text, f"Test Failed: Status for '{target_user}' did not update to 'Verified'."