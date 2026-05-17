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


def test_tp_09_007_invalid_dataset_values_fails_on_bug(admin_driver):
    driver = admin_driver
    wait = WebDriverWait(driver, 10)
    
    # Navigate to the "Weather Data" module
    weather_data_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Weather Data') and not(contains(text(), 'Management'))]")))
    weather_data_link.click()
    time.sleep(2)
    
    try:
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading weather data...')]")))
        wait.until_not(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Loading company locations...')]")))
    except Exception:
        pass
    
    # ==========================================
    # PART 1: OPEN FORM & FILL OUT-OF-RANGE DATA
    # ==========================================
    
    add_record_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add New Record')]")))
    add_record_btn.click()
    
    date_input = wait.until(EC.visibility_of_element_located((By.ID, "date")))
    
    driver.execute_script("""
        var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(arguments[0], '2026-05-15');
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, date_input)
    
    # Enter an out-of-range Temperature
    temp_input = driver.find_element(By.ID, "temperature")
    temp_input.clear()
    temp_input.send_keys("-60")
    
    # Enter a negative humidity (invalid)
    humidity_input = driver.find_element(By.ID, "humidity")
    humidity_input.clear()
    humidity_input.send_keys("-10")
    
    # Enter a negative rainfall (invalid)
    rainfall_input = driver.find_element(By.ID, "rainfall")
    rainfall_input.clear()
    rainfall_input.send_keys("-5")
    
    location_input = driver.find_element(By.ID, "location")
    location_input.clear()
    location_input.send_keys("Kuala Lumpur")
    
    area_select = driver.find_element(By.ID, "companyLocationId")
    area_select.click()
    first_area_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='companyLocationId']/option[2]")))
    first_area_option.click()
    
    # ==========================================
    # PART 2: SUBMIT AND STRICTLY VERIFY UI
    # ==========================================
    
    submit_btn = driver.find_element(By.XPATH, "//form//button[contains(., 'Add Record')]")
    submit_btn.click()
    
    # Wait a brief moment to see how the React UI reacts
    time.sleep(1)
    
    # ASSERTION 1: The form/modal should STILL be visible because submission failed.
    # If the UI bug causes the form to vanish, this assertion will catch it and fail the test.
    form_elements = driver.find_elements(By.ID, "temperature")
    assert len(form_elements) > 0 and form_elements[0].is_displayed(), \
        "DEFECT FOUND: SRS (TC-09-007) requires the system to display validation errors. Instead, the form abruptly closed/disappeared without showing the user what went wrong."

    # ASSERTION 2: Ensure an explicit error message is displayed on the screen
    try:
        error_alert = driver.find_element(By.XPATH, "//div[contains(@class, 'text-red-800')]")
        assert error_alert.is_displayed(), "Test Failed: The form stayed open, but no explicit error banner was displayed for the invalid data."
    except Exception:
        pytest.fail("Test Failed: The form stayed open, but the system failed to display a visible error message.")