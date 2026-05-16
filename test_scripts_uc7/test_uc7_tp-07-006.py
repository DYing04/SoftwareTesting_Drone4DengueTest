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


def test_tp_07_006_remove_user(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to User Management
    user_management_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'User Management')]")))
    user_management_link.click()
    
    # Wait a moment to ensure the table and user data fetch is complete
    time.sleep(2)
    
    target_user = "Jason"
    
    # ==========================================
    # PART 1: LOCATE AND CLICK DELETE
    # ==========================================
    
    # Search for the target user to easily isolate their row
    search_bar = wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Search users...']")))
    search_bar.clear()
    search_bar.send_keys(target_user)
    time.sleep(1)
    
    # Locate the Delete button for the specific user
    delete_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//tr[contains(., '{target_user}')]//button[contains(@class, 'text-red-500')]"
    )))
    delete_button.click()
    
    # ==========================================
    # PART 2: CONFIRM DELETION
    # ==========================================
    
    # Handle the Confirmation Modal
    confirm_delete_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Delete') and contains(@class, 'bg-red-600')]")))
    confirm_delete_btn.click()
    
    # Handle the Deletion Success Dialog
    great_btn_after_delete = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Great!')]")))
    great_btn_after_delete.click()
    
    # Wait for the success dialog to disappear
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//h3[contains(text(), 'Success!')]")))
    
    # ==========================================
    # PART 3: VERIFY REMOVAL
    # ==========================================
    
    time.sleep(1) # Allow React state to update the table
    
    # Clear the search bar and search again to ensure a fresh check
    search_bar.clear()
    search_bar.send_keys(target_user)
    time.sleep(1)   
    
    # Verify the row containing the user is no longer present in the DOM
    rows_with_user = driver.find_elements(By.XPATH, f"//table//tbody//tr[contains(., '{target_user}')]")
    
    # Assert that the list is empty (length is 0)
    assert len(rows_with_user) == 0, f"Test Failed: User '{target_user}' was not successfully permanently removed from the list."