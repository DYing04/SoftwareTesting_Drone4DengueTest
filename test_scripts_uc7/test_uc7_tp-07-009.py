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


def test_tp_07_009_exception_save_fails(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    time.sleep(2)
    
    # ==========================================
    # PART 1: OPEN EDIT MODAL
    # ==========================================
    
    # Click Edit on the first available user
    edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//table//tbody//tr[1]//button[contains(@class, 'text-accent-blue')]")))
    edit_button.click()
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[text()='Update User']")))
    
    # Modify a field to trigger an update (e.g., Name)
    name_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter full name']")))
    name_field.send_keys(" (Updated)")
    
    # ==========================================
    # PART 2: SIMULATE NETWORK FAILURE
    # ==========================================
    
    # Disconnect the network to simulate backend failure
    driver.set_network_conditions(
        offline=True,
        latency=5,
        download_throughput=500 * 1024,
        upload_throughput=500 * 1024
    )
    
    try:
        # Click Update User
        update_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Update User')]")))
        update_btn.click()
        
        # ==========================================
        # PART 3: VERIFY ERROR MESSAGE
        # ==========================================
        
        # The system should catch the fetch failure and display it in the red error div inside the modal
        error_msg = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'text-red-700')]")))
        assert error_msg.is_displayed(), "Test Failed: System did not display an error message when the save operation failed."
        
    finally:
        # Always restore network conditions so subsequent tests don't fail
        driver.set_network_conditions(
            offline=False,
            latency=5,
            download_throughput=500 * 1024,
            upload_throughput=500 * 1024
        )
