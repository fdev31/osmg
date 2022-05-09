import os
from time import sleep
import unittest
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import JavascriptException


class EndOfGameError(Exception):
    pass


from config import HOST
from common import getStream, pretty

HOME_INDEX = 0
NB_PLAYERS = 3

endOfGame = False


def getId(driver):
    return driver.execute_script("return application.myId")


def getPlayerData(driver, attr):
    return driver.execute_script(
        "return application.playersData[application.myId].%s" % attr
    )


def diceValue(driver, value=None):
    if value is None:
        return driver.execute_script("return application.$refs.mydice.getDiceValues()")
    driver.execute_script(
        "application.player_advance('%s')" % ("".join(str(x) for x in value))
    )


def waitEvent(names: list, maxTime=None):
    global endOfGame
    print("Waiting for %s" % (" or ".join(names)))
    while True:
        events = getStream()
        for e in events:
            if e.isA("endOfGame"):
                endOfGame = True
            print(endOfGame, "got %s" % pretty(e))
        for evt in events:
            if any(evt.isA(name) for name in names):
                sleep(0.2)
                return evt
        sleep(0.150)
        if maxTime is not None:
            maxTime -= 0.15
            if maxTime <= 0:
                return False


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
    setInputText(driver.find_element(By.TAG_NAME, "input"), "S. Anita")
    sleep(1)
    driver.execute_script("window.scrollTo(0, 100)")

    # click game tile
    but = driver.find_elements(By.CLASS_NAME, "gamebutton")[gameIndex]
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
        sleep(0.5)
        lobby_url = self.driver.find_element(By.ID, "link").get_attribute("value")
        lobby_name = lobby_url.rsplit("/", 1)[1]
        getStream(lobby_name)
        shot(self.driver, "lobby")
        # other player join game
        for drv in self.drv[1:]:
            drv.get(lobby_url)
        print("everybody in lobby", getStream())
        self.pids = [getId(drv) for drv in self.drv]
        for i, drv in enumerate(self.drv[1:]):
            setInputText(
                drv.find_element(By.TAG_NAME, "input"), "Player %d" % i, delete=10
            )
            shot(drv, "login%d" % (i + 2))
            drv.find_elements(By.TAG_NAME, "button")[0].click()

        print("About to start")
        shot(self.driver, "lobby_full")

        # start game
        for drv in self.drv:
            drv.find_elements(By.CLASS_NAME, "mainAction")[0].click()

        sleep(5)
        print("Start")

        def isThrowValid(curDice, distance):
            val = int("".join(str(x) for x in curDice))
            return distance - val >= 0

        def playerTurn(drv):
            distance = getPlayerData(drv, "distance")
            if distance > 0:
                try:
                    drv.find_elements(By.CLASS_NAME, "mainAction")[0].click()
                except IndexError:
                    raise EndOfGameError("No main action on this screen")
                sleep(1)
                dices = diceValue(drv)
                print("Remains %d, choices: %s" % (distance, dices))
                dices.sort(reverse=True)
                if isThrowValid(dices, distance):
                    diceValue(drv, dices)
                else:
                    dices.sort()
                    if (isThrowValid(dices, distance)) or random.randint(0, 50) == 1:
                        diceValue(drv, dices)
                    else:
                        diceValue(drv, [0])
                waitEvent(["varUpdate"])
                sleep(0.1)
            sleep(0.2)

        evt = waitEvent(["start"])

        assert "max" in evt
        assert "min" in evt

        for n in range(100):
            try:
                for drv in self.drv:
                    playerTurn(drv)
            except EndOfGameError as e:
                print(f"game end detected", e)
                sleep(1)
                makeShots(self.drv, "end_game")
                break
            else:
                if n == 6:
                    makeShots(self.drv, "mid_game")

        for elt in getStream():
            print(pretty(elt))

        if not endOfGame:
            waitEvent(["endOfGame"], maxTime=5)

        assert endOfGame is True, "Game didn't finish !!"

    def tearDown(self):
        if "WAIT" in os.environ:
            input("Press some key to continue...")
        for drv in self.drv:
            drv.close()


if __name__ == "__main__":
    unittest.main()
