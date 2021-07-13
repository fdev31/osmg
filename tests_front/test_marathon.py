import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from config import HOST

HOME_INDEX = 0

def setInputText(inp, value):
    inp.click()
    inp.send_keys([Keys.CONTROL, "a"])
    inp.send_keys(Keys.BACK_SPACE)
    inp.send_keys(value)

def create_game(driver, gameIndex):
    driver.get("http://" + HOST)

    # change login
    setInputText(driver.find_element_by_tag_name("input"), "S. Anita")

    # click game tile
    driver.find_elements_by_class_name('gamebutton')[gameIndex].click()

class MarathonTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver2 = webdriver.Chrome()

    def test_game(self):
        create_game(self.driver, HOME_INDEX)
        lobby_url = self.driver.find_element_by_id('link').get_attribute('value')
        # other player join game
        self.driver2.get(lobby_url)
        setInputText(self.driver2.find_element_by_tag_name("input"), "pif paf")
        self.driver2.find_element_by_tag_name("button").click()
        # start game
        self.driver.find_elements_by_tag_name("button")[1].click()
        self.driver2.find_elements_by_tag_name("button")[1].click()

        time.sleep(1)
        for n in range(20):
            try:
                self.driver.find_elements_by_tag_name("button")[0].click()
                time.sleep(0.1)
                self.driver.find_elements_by_tag_name("button")[0].click()
                time.sleep(0.5)
                self.driver2.find_elements_by_tag_name("button")[0].click()
                time.sleep(0.1)
                self.driver2.find_elements_by_tag_name("button")[0].click()
                time.sleep(0.5)
            except IndexError:
                break

    def tearDown(self):
        input("Press some key to exit")
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
