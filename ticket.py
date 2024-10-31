from config import config
from config.utils.basic import Basic
from config.utils.log import logger
import time
import random

class Ticket(Basic):
    
    def __init__(self, driver):
        super().__init__(driver)
        
    def open_page(self, page):
        self.driver.get(page)
        
    def go_to_login_page(self):
        self.open_page(config.OPENED_PAGE)
        
    def login(self):
        try:
            time.sleep(1)
            self.enter_message(config.EMAIL, id='signInFormUsername', driver=self.driver)
            time.sleep(1)
            self.enter_message(config.PASSWORD, id='signInFormPassword', driver=self.driver)
            time.sleep(1)
            self.click_el(name='signInSubmitButton')
            time.sleep(1)
                       
        except Exception as e:
            logger.error(e)
            
    def go_to_ticket_page(self):
        time.sleep(1)
        self.open_page(config.TICKET_PAGE)
        