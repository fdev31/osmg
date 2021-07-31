import os
from time import sleep
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from config import HOST

HOME_INDEX = 0
NB_PLAYERS = 6

if not os.path.exists("screenshots"):
    os.mkdir("screenshots")


def shot(driver, name):
    driver.save_screenshot(os.path.join("screenshots", f"marathon_{name}.png"))


def makeShots(drivers, suffix):
    shot(drivers[0], "ff_end_screen")
    for i, drv in enumerate(drivers[1:]):
        shot(drv, "ch%d_%s" % (i + 2, suffix))


def setInputText(inp, value, delete=None):
    inp.click()
    sleep(0.1)
    if delete:
        inp.send_keys([Keys.BACKSPACE] * delete)
    else:
        inp.send_keys([Keys.CONTROL, "a"])
    sleep(0.1)
    inp.send_keys(value)


def create_game(driver, gameIndex):
    driver.get("http://" + HOST)

    # change login
    setInputText(driver.find_element_by_tag_name("input"), "S. Anita")
    sleep(1)

    # click game tile
    but = driver.find_elements_by_class_name("gamebutton")[gameIndex]
    but.click()


class MarathonTest(unittest.TestCase):
    def setUp(self):
        self.drv = [webdriver.Firefox()]
        sleep(1)
        for n in range(1, NB_PLAYERS):
            self.drv.append(webdriver.Chrome())
            sleep(1)
        sleep(0.5)

    @property
    def driver(self):
        return self.drv[0]

    def test_game(self):
        create_game(self.driver, HOME_INDEX)
        sleep(1)
        lobby_url = self.driver.find_element_by_id("link").get_attribute("value")
        shot(self.driver, "login1")
        # other player join game
        for drv in self.drv[1:]:
            drv.get(lobby_url)
        sleep(0.5)
        for i, drv in enumerate(self.drv[1:]):
            setInputText(
                drv.find_element_by_tag_name("input"), "Player %d" % i, delete=10
            )
            shot(drv, "login%d" % (i + 2))
            drv.find_elements_by_tag_name("button")[0].click()

        print("About to start")
        sleep(1)

        # start game
        for drv in self.drv:
            drv.find_elements_by_class_name("mainAction")[0].click()

        sleep(8)
        print("Start")

        def playerTurn(drv):
            drv.find_elements_by_class_name("mainAction")[0].click()
            sleep(0.5)
            drv.find_elements_by_class_name("mainAction")[0].click()
            sleep(0.5)

        for n in range(20):
            try:
                for drv in self.drv:
                    playerTurn(drv)
                sleep(0.5)
            except IndexError as e:
                print("game end detected", e)
                makeShots(self.drv, "end_game")
                break
            else:
                if n == 10:
                    makeShots(self.drv, "mid_game")
            sleep(0.1 * NB_PLAYERS)

        makeShots(self.drv, "end_screen")

    def tearDown(self):
        if "WAIT" in os.environ:
            input("Press some key to continue...")
        for drv in self.drv:
            drv.close()


if __name__ == "__main__":
    unittest.main()
