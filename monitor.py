import undetected_chromedriver as uc
import time
from config import config
import random

from config.utils.log import logger
from ticket import Ticket

def init_driver():
    profile = {
        "profile.default_content_setting_values.notification": 2 # block notification
    }
    chrome_options = uc.ChromeOptions()
    chrome_options.add_experimental_option('prefs', profile)
    chrome_options.add_argument("--incognito")
    
    driver_path =  'chromedriver-win64/chromedriver.exe'
    
    driver = uc.Chrome(excutable_path=driver_path, options=chrome_options)
    driver.implicitly_wait(1)
    driver.delete_all_cookies()
    return driver
           
def monitor():
    try:
        driver = init_driver()
        ticket = Ticket(driver)
        # ticket.go_to_login_page()
        # ticket.wait_for_loading()
        # ticket.login()
        # ticket.wait_for_loading()
        ticket.go_to_ticket_page()
        ticket.wait_for_loading()
        ticket.select_ticket(driver=driver)
        ticket.wait_for_loading()
        ticket.verify_captcha(driver=driver)
        
        input()
              
    except Exception as e:
        logger.error(f'Monitor runtime error. {e}')
        if driver is not None:
            driver.quit()
        monitor()

        
if __name__ == "__main__":
    monitor()