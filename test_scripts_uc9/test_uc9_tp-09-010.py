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



def test_tp_09_010_admin_cancels_upload(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    time.sleep(2)
    
    # Wait for the data fetching to resolve
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass

    # ==========================================
    # PART 1: INITIATE UPLOAD / FORM ENTRY
    # ==========================================
    
    # Click "Add New Record" to open the manual entry form
    add_record_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add New Record')]")))
    add_record_btn.click()
    
    # Wait for the form to appear
    date_input = wait.until(EC.visibility_of_element_located((By.ID, "date")))
    
    # Type some data into the form to ensure it gets discarded later
    temp_input = driver.find_element(By.ID, "temperature")
    temp_input.clear()
    temp_input.send_keys("35.5")
    
    # ==========================================
    # PART 2: CANCEL THE OPERATION
    # ==========================================
    
    # Click the Cancel button
    cancel_btn = driver.find_element(By.XPATH, "//form//button[contains(., 'Cancel')]")
    cancel_btn.click()
    
    # ==========================================
    # PART 3: VERIFY ABORTION & RETURN TO DASHBOARD
    # ==========================================
    
    # 1. Verify the form completely disappears
    wait.until(EC.invisibility_of_element_located((By.ID, "date")))
    
    # 2. Verify no success or error banners popped up (proving no save attempt was made)
    alerts = driver.find_elements(By.XPATH, "//div[contains(@role, 'alert')]")
    assert len(alerts) == 0, "Test Failed: An alert banner was displayed, indicating a process might have run despite clicking Cancel."
    
    # 3. Verify we are back on the main dashboard by checking if the "Add New Record" button is visible again
    assert add_record_btn.is_displayed(), "Test Failed: The system did not return to the weather dashboard state after cancelling."