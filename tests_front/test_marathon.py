import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from config import HOST

HOME_INDEX = 0

if not os.path.exists('screenshots'):
    os.mkdir('screenshots')

def shot(driver, name):
    driver.save_screenshot(os.path.join("screenshots", f'marathon_{name}.png') )

def setInputText(inp, value, delete=None):
    inp.click()
    time.sleep(0.1)
    if delete:
        inp.send_keys([Keys.BACKSPACE]*delete)
    else:
        inp.send_keys([Keys.CONTROL, "a"])
    time.sleep(0.1)
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
        shot(self.driver, "login1")
        lobby_url = self.driver.find_element_by_id('link').get_attribute('value')
        time.sleep(1)
        # other player join game
        self.driver2.get(lobby_url)
        time.sleep(0.5)
        setInputText(self.driver2.find_element_by_tag_name("input"), "pif paf", delete=10)
        shot(self.driver2, "login2")
        self.driver2.find_elements_by_tag_name("button")[0].click()
        time.sleep(1)
        # start game
        self.driver.find_elements_by_tag_name("button")[3].click()
        self.driver2.find_elements_by_tag_name("button")[3].click()

        time.sleep(1)
        shot(self.driver, "ff_game")
        shot(self.driver2, "ch_game")
        but_idx = 2
        for n in range(20):
            try:
                self.driver.find_elements_by_tag_name("button")[but_idx].click()
                time.sleep(0.1)
                self.driver.find_elements_by_tag_name("button")[but_idx].click()
                time.sleep(0.5)
                self.driver2.find_elements_by_tag_name("button")[but_idx].click()
                time.sleep(0.1)
                self.driver2.find_elements_by_tag_name("button")[but_idx].click()
                time.sleep(0.5)
            except IndexError:
                shot(self.driver, "ff_end_game")
                shot(self.driver2, "ch_end_game")
                break
            else:
                if n == 10:
                    shot(self.driver, "ff_mid_game")
                    shot(self.driver2, "ch_mid_game")
        shot(self.driver, "ff_end_screen")
        shot(self.driver2, "ch_end_screen")

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
