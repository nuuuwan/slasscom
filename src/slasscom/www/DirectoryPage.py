import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from utils import Log

log = Log('DirectoryPage')


class DirectoryPage:
    URL = "https://www.slasscom.lk/directory"

    def __init__(self):
        self.driver = None

    def open(self):
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.get(self.URL)
        self.driver.set_window_size(3200, 3200)
        log.debug(f'🌍 Opened {self.URL}...')

    def quit(self):
        self.driver.quit()
        log.debug('🚪 Closed the browser.')

    def click_next(self):
        log.debug('🖱️ Clicking next...')
        time.sleep(2)
        button_next = self.driver.find_element(By.ID, 'next')
        button_next.click()

    def get_company_d(self, div_member_card) -> dict:
        elem_list = div_member_card.find_elements(
            By.CLASS_NAME, 'uwp-user-meta'
        )
        text_list = [elem.text for elem in elem_list]
        if len(text_list) == 9:
            text_list = text_list[1:]

        logo_image_url = (
            elem_list[0].find_element(By.TAG_NAME, 'img').get_attribute('src')
        )

        [
            name,
            core_business_focus,
            service_sectors,
            address,
            telephone,
            email,
            website,
        ] = text_list[1:]

        address = address.replace('\n', ' ').strip()

        return dict(
            name=name,
            logo_image_url=logo_image_url,
            core_business_focus=core_business_focus,
            service_sectors=service_sectors,
            address=address,
            telephone=telephone,
            email=email,
            website=website,
        )

    def get_company_d_list(self) -> list[dict]:
        if not self.driver:
            raise Exception('Webpage not opened!')

        div_member_card_list = self.driver.find_elements(
            By.CLASS_NAME, 'member_card'
        )
        log.debug(f'Found {len(div_member_card_list)} member cards')

        company_d_list = []
        for div_member_card in div_member_card_list:
            company_d = self.get_company_d(div_member_card)
            if not company_d['name']:
                self.click_next()
                company_d = self.get_company_d(div_member_card)

            log.debug(company_d)
            company_d_list.append(company_d)
        n = len(company_d_list)
        log.debug(f'Extracted {n} company details')
        return company_d_list
