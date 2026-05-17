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


def test_tp_09_005_verify_audit_logging_fails_on_bug(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # 1. Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    
    time.sleep(2)
    
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass

# ==========================================
    # PART 1: EDIT A HISTORICAL RECORD
    # ==========================================
    
    # Target a record from the past
    historical_date = "15/5/2026"
    target_row_xpath = f"//table//tbody//tr[contains(., '{historical_date}')]"
    
    wait.until(EC.presence_of_element_located((By.XPATH, target_row_xpath)))
    edit_button = wait.until(EC.element_to_be_clickable((By.XPATH, f"{target_row_xpath}//button[1]")))
    edit_button.click()
    
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Edit Weather Record')]")))
    
    # ==========================================
    # PART 2: FIX STEP="0.1" VALIDATION ERRORS
    # ==========================================
    
    # Ensure Temperature is rounded to 1 decimal place + increment it
    temp_input = wait.until(EC.visibility_of_element_located((By.ID, "modal-temperature")))
    current_temp = float(temp_input.get_attribute("value") or 0)
    temp_input.clear()
    temp_input.send_keys(str(round(current_temp + 0.1, 1)))
    
    # Ensure Humidity is rounded to 1 decimal place to bypass HTML5 validation
    humidity_input = driver.find_element(By.ID, "modal-humidity")
    current_humidity = float(humidity_input.get_attribute("value") or 0)
    humidity_input.clear()
    humidity_input.send_keys(str(round(current_humidity, 1)))

    # Ensure Rainfall is rounded to 1 decimal place
    rainfall_input = driver.find_element(By.ID, "modal-rainfall")
    current_rainfall = float(rainfall_input.get_attribute("value") or 0)
    rainfall_input.clear()
    rainfall_input.send_keys(str(round(current_rainfall, 1)))
    
    # ==========================================
    # PART 3: SUBMIT AND WAIT
    # ==========================================
    
    # Click Update Record
    update_btn = driver.find_element(By.XPATH, "//div[contains(@class, 'fixed')]//button[contains(., 'Update Record')]")
    update_btn.click()
    
    # Wait for modal to close
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//*[contains(text(), 'Edit Weather Record')]")))
    time.sleep(2) # Allow React to refresh the table
    
    # ==========================================
    # PART 4: ASSERTION (THIS WILL FAIL ON THE BUG)
    # ==========================================
    
    date_element_xpath = f"{target_row_xpath}//td[1]//div[contains(@class, 'flex-col')]/span[1]"
    displayed_date_text = wait.until(EC.visibility_of_element_located((By.XPATH, date_element_xpath))).text
    
    current_time = datetime.now()
    expected_system_date = f"{current_time.day}/{current_time.month}/{current_time.year}"
    
    # This will now fail correctly because the UI will show 15/5/2026 instead of today's date
    assert displayed_date_text == expected_system_date, f"DEFECT FOUND: SRS (TC-09-005) requires audit timestamp to match current system date. Expected '{expected_system_date}', but UI incorrectly displayed the old weather date '{displayed_date_text}'."