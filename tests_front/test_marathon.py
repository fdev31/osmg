import os
from time import sleep
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import JavascriptException
from config import HOST
from common import getStream, pretty

HOME_INDEX = 0
NB_PLAYERS = 3


def getId(driver):
    return driver.execute_script("return window.lobby.myId")


def getPlayerData(driver, attr):
    return driver.execute_script("return marathon.playersData[marathon.myId].%s" % attr)


def waitEvent(names):
    print("Waiting for %s" % (" or ".join(names)))
    while True:
        events = getStream()
        for e in events:
            print(" got %s" % pretty(e))
        for evt in events:
            if any(evt.isA(name) for name in names):
                sleep(0.2)
                return evt
        sleep(0.150)


if not os.path.exists("screenshots"):
    os.mkdir("screenshots")


def shot(driver, name):
    driver.save_screenshot(os.path.join("screenshots", f"marathon_{name}.png"))


def makeShots(drivers, suffix):
    shot(drivers[0], suffix + "_ff")
    for i, drv in enumerate(drivers[1:]):
        shot(drv, "%s_ch%d" % (suffix, i + 2))


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
        for n in range(1, NB_PLAYERS):
            self.drv.append(webdriver.Chrome())
            sleep(0.5)

    @property
    def driver(self) -> webdriver.Chrome:
        return self.drv[0]

    def test_game(self):
        create_game(self.driver, HOME_INDEX)
        sleep(1)
        lobby_url = self.driver.find_element_by_id("link").get_attribute("value")
        lobby_name = lobby_url.rsplit("/", 1)[1]
        getStream(lobby_name)
        shot(self.driver, "lobby")
        # other player join game
        for drv in self.drv[1:]:
            drv.get(lobby_url)
        sleep(0.5)
        print("everybody in lobby", getStream())
        self.pids = [getId(drv) for drv in self.drv]
        for i, drv in enumerate(self.drv[1:]):
            setInputText(
                drv.find_element_by_tag_name("input"), "Player %d" % i, delete=10
            )
            shot(drv, "login%d" % (i + 2))
            drv.find_elements_by_tag_name("button")[0].click()

        print("About to start")
        sleep(1)
        shot(self.driver, "lobby_full")

        # start game
        for drv in self.drv:
            drv.find_elements_by_class_name("mainAction")[0].click()

        sleep(8)
        print("Start")

        def playerTurn(drv):
            if getPlayerData(drv, "distance") > 0:
                drv.find_elements_by_class_name("mainAction")[0].click()
                sleep(0.1)
                drv.find_elements_by_class_name("mainAction")[0].click()
                waitEvent(["varUpdate"])
                sleep(0.1)

        waitEvent(["start"])
        for n in range(100):
            try:
                for drv in self.drv:
                    playerTurn(drv)
            except JavascriptException:
                print("game end detected")
                sleep(1)
                makeShots(self.drv, "end_game")
                break
            else:
                if n == 6:
                    makeShots(self.drv, "mid_game")

        for elt in getStream():
            print(pretty(elt))

    def tearDown(self):
        if "WAIT" in os.environ:
            input("Press some key to continue...")
        for drv in self.drv:
            drv.close()


if __name__ == "__main__":
    unittest.main()
