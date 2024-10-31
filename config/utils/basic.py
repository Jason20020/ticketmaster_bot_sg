from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from config.utils.log import logger
from config import config
from twocaptcha import TwoCaptcha
import time
import traceback
import random
import os
import requests
from selenium.webdriver.support.ui import Select
import pytesseract
from PIL import Image

class Basic:
    def __init__(self, driver):
        self.driver = driver
        
    def click_el(self, xpath=None, id=None, name=None, text=None):
        locator = None
        if xpath:
            locator = (By.XPATH, xpath)
        elif id:
            locator = (By.ID, id)
        elif name:
            locator = (By.NAME, name)
        else:
            locator = (By.XPATH, "//*[contains(text(), '{}')]".format(text))
        elements = WebDriverWait(self.driver, 10).until( ec.presence_of_all_elements_located(locator), message="No element")
        
        for element in elements:
            try:
                WebDriverWait(self.driver, 0.2).until(ec.element_to_be_clickable(element)).click()
                print("Clicked on an element.")
                break 
            except:
                continue
        else:
            print("No clickable elements found.")
        
    def wait_for_loading(self):
        WebDriverWait(self.driver, 10).until(ec.invisibility_of_element_located((By.ID, "overlay")))
        
    def enter_message(self, message, xpath=None, id=None, name=None, text=None, driver=None):
        if xpath:
            locator = (By.XPATH, xpath)
        elif id: 
            locator = (By.ID, id)
        elif name:
            locator = (By.NAME, name)
        else:
            locator = (By.XPATH, "//*[contains(text(), '{}')]".format(text))
        elements = WebDriverWait(self.driver, 10).until(ec.presence_of_all_elements_located(locator), message="No element {}".format(locator))
        
        element = None

        for index, elem in enumerate(elements):
            try:
                WebDriverWait(self.driver, 2).until(ec.visibility_of(elem))
                element = elem
                logger.info(f"Element {index} with ID '{elem.get_attribute('id')}' is visible")
                break
            except:
                logger.info(f"Element {index} with ID '{elem.get_attribute('id')}' is not visible")
                continue
        
        actions = ActionChains(driver)

        time.sleep(random.uniform(1, 2))

        actions.move_to_element(element).click().perform()

        for char in message:
            if random.random() < 0.1: 
                wrong_char = chr(random.randint(97, 122)) 
                actions.send_keys(wrong_char).perform()
                time.sleep(0.2)
                actions.send_keys(Keys.BACKSPACE).perform()
            actions.send_keys(char).perform()
            time.sleep(random.uniform(0.1, 0.4)) 
            
        time.sleep(random.uniform(0, 3))
         
    def wait_of_secs(self, driver=None, secs=1):
        WebDriverWait(driver, secs)
        
    def take_page_screenshot(self, driver=None, attempt=0):
        if(attempt == 0):
            # getting captcha modal
            iframe = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//iframe[@title='Verify Registration' or @title='Verify Selection']")),
                message="iframe not found"
            )
            # switch to modal page
            driver.switch_to.frame(iframe)

        # make sure the captcha is fully loader
        WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located((By.ID, 'submit')),
            message="Submit icon not visible after waiting"
        )
        body = driver.find_element(By.TAG_NAME, "body")

        # taking screenshot for 2captcha
        time.sleep(random.uniform(3, 7))
        body.screenshot("full_page_image.png")
        
        logger.info(f'Screenshot Taken')
        
    def verify_captcha(self, driver=None):
        # click verify button to solve captcha
        self.click_el(id='btnVerify')
        
        self.solve_captcha(driver=driver)
        
        driver.switch_to.default_content()
        self.click_el(id='btnSubmit')

    def solve_captcha(self, driver=None, max_attempts=5):
        attempt = 0
        while attempt < max_attempts:
            try:             
                # Take screenshot
                self.take_page_screenshot(driver=self.driver, attempt=attempt)

                api_key = os.getenv('APIKEY_2CAPTCHA', config.TWO_CAPTCHA_KEY)
                solver = TwoCaptcha(api_key)
                image = 'full_page_image.png'
                
                logger.info(f'Solving Captcha')
                result = solver.coordinates(image)
                logger.info(f"Captcha answer received")
                code = result.get('code')

                if code:
                    coordinates = code.replace('coordinates:', '').split(';')
                    coordinates_list = []

                    for coord in coordinates:
                        time.sleep(random.uniform(1, 2))
                        x, y = coord.split(',')
                        x_value = int(x.split('=')[1])
                        y_value = int(y.split('=')[1])
                        coordinates_list.append((x_value, y_value))

                        # Click using JavaScript at the specified coordinates
                        logger.info(f"Clicking at answer")
                        driver.execute_script(f"document.elementFromPoint({x_value}, {y_value}).click()")
                        time.sleep(random.uniform(1, 2))
                    # Click the submit button within the iframe
                    self.click_el(id='submit')   
                    time.sleep(random.uniform(8, 12))

                    # Check if alert is present
                    try:
                        alert = driver.switch_to.alert
                        alert.accept()
                        logger.warning("Alert detected and accepted, retrying captcha verification.")
                        attempt += 1
                    except NoAlertPresentException:
                        logger.info("No alert detected, captcha verification completed successfully.")
                        return  # Captcha solved successfully, exit function

                else:
                    error_code = result.get('code')
                    logger.error(f"TwoCaptcha failed with error code: {error_code}")
                    if error_code == 'ERROR_WRONG_USER_KEY':
                        logger.error("Invalid API key.")
                    elif error_code == 'ERROR_CAPTCHA_UNSOLVABLE':
                        logger.error("Captcha could not be solved by the workers.")

                    attempt += 1

            except UnexpectedAlertPresentException:
                # Handle unexpected alert that might appear during the process
                alert = driver.switch_to.alert
                alert.accept()
                logger.warning("Unexpected alert detected and accepted, retrying captcha verification.")
                attempt += 1

            except Exception as e:
                logger.error(f"Failed to solve captcha: {str(e)}")
                logger.error(traceback.format_exc())
                attempt += 1
                
    def select_ticket(self, driver=None):
        ids_to_check = ["field_PA8", "field_PA7", "field_PB9"]

        for element_id in ids_to_check:
            clickable_element = WebDriverWait(self.driver, 3600).until(
                ec.presence_of_element_located((By.ID, element_id))
            )
            
            element_class = clickable_element.get_attribute('class')
            if element_class and 'empty' in element_class:
                print(f"Skipping ID: {element_id} as it has class 'empty'")
                continue

            driver.execute_script("""
                var event = new MouseEvent('click', {
                    bubbles: true,
                    cancelable: true,
                    view: window
                });
                arguments[0].dispatchEvent(event);
            """, clickable_element)
            print(f"Click ID: {element_id}")
            break
        
        ids_to_check = ["TicketForm_ticketPrice_001", "TicketForm_ticketPrice_002"]

        selected_element = None
        for element_id in ids_to_check:
            try:
                selected_element = WebDriverWait(self.driver, 0.5).until(
                    ec.presence_of_element_located((By.ID, element_id))
                )
                print(f"Found ID: {element_id}")
                break 
            except:
                print(f"Element ID {element_id} not exist")

        if selected_element.tag_name.lower() == "select":
            select = Select(selected_element)
            select.select_by_index(3)
            print("成功选择第三个选项")
        else:
            print("Not Found elements select")    
        
        self.click_el(id="autoMode")
        
    def verify_captcha(self, driver=None):
        captcha_element = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.ID, "TicketForm_verifyCode-image"))
        )

        captcha_element.screenshot("captcha_image.png")
        try:
            pytesseract.pytesseract.tesseract_cmd = r'C:\Users\jason.chai\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
            time.sleep(0.5)
            image = Image.open("captcha_image.png")

            captcha_text = pytesseract.image_to_string(image)
            print(f"识别到的验证码是: {captcha_text}")
            
            # WebDriverWait(driver, 5).until(ec.alert_is_present())
            # alert = driver.switch_to.alert
            # alert.accept()  
            # print("Alert Closed")
    
            captcha_input = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.ID, "TicketForm_verifyCode"))
            )
            captcha_input.send_keys(captcha_text)
            
            label_element = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((By.XPATH, "//label[@for='TicketForm_agree']"))
            )

            actions = ActionChains(driver)
            actions.move_to_element(label_element).click().perform()

            submit_button = WebDriverWait(self.driver, 10).until(
                ec.element_to_be_clickable((By.XPATH, "//button[@type='submit' and text()='Submit']"))
            )
            submit_button.click()

        except Exception as e:
            print(f"识别验证码失败: {e}")