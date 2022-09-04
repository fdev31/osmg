import os
import unittest
from time import sleep

from common import ctx, getId, getStream, resetStream, waitEvent
from config import HOST
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class EndOfGameError(Exception):
    pass


resetStream()


def teardown_module():
    resetStream()


HOME_INDEX = 2
NB_PLAYERS = 2

if not os.path.exists("screenshots"):
    os.mkdir("screenshots")


def shot(driver, name):
    driver.save_screenshot(os.path.join("screenshots", f"atakks_{name}.png"))


def makeShots(drivers, suffix):
    shot(drivers[0], suffix + "_ff")
    for i, drv in enumerate(drivers[1:]):
        shot(drv, "%s_ch%d" % (suffix, i + 2))


def setInputText(inp, value, delete=30):
    sleep(1)
    inp.click()
    sleep(0.5)
    if delete:
        inp.send_keys([Keys.BACKSPACE] * delete)
    else:
        inp.send_keys([Keys.CONTROL, "a"])
    sleep(0.5)
    inp.send_keys(value)


def create_game(driver, gameIndex):
    driver.get("http://" + HOST)

    # change login
    setInputText(driver.find_element(By.TAG_NAME, "input"), "S. Anita")
    sleep(1)
    driver.execute_script("window.scrollTo(0, 100)")

    # click game tile
    but = driver.find_elements(By.CLASS_NAME, "tile")[gameIndex]
    but.click()


class AtakksTest(unittest.TestCase):
    def setUp(self):
        opts = ChromeOptions()
        opts.add_argument("--no-sandbox")
        """
        opts.add_argument("--test-type")
        opts.add_argument("--verbose")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        """

        self.drv = [webdriver.Chrome(options=opts)]
        for n in range(1, NB_PLAYERS):
            self.drv.append(webdriver.Chrome(options=opts))

    @property
    def driver(self) -> webdriver.Chrome:
        return self.drv[0]

    def test_game(self):
        create_game(self.driver, HOME_INDEX)
        sleep(1)
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
            setInputText(drv.find_element(By.TAG_NAME, "input"), "Player %d" % i)
            shot(drv, "login%d" % (i + 2))
            drv.find_elements(By.TAG_NAME, "button")[0].click()

        print("About to start")
        shot(self.driver, "lobby_full")

        # start game
        for drv in self.drv:
            drv.find_elements(By.CLASS_NAME, "btn-main")[0].click()

        sleep(5)
        print("Start")

        players_pos = {
            0: 0,
            1: 0,
        }

        def playerTurn(drv, idx):
            print("INDEX", idx)

            nb_pawns = len(drv.find_elements(By.CSS_SELECTOR, ".pawn.piece"))
            total_slots = len(drv.find_elements(By.CSS_SELECTOR, ".pawn:not(.piece)"))
            done = False
            while not done:
                i = players_pos[idx]
                try:
                    drv.find_elements(By.CSS_SELECTOR, ".pawn:not(.piece)")[
                        total_slots - i if idx else i
                    ].click()
                except Exception:
                    print("failed %d" % i)
                else:
                    sleep(0.1)
                    if (
                        len(drv.find_elements(By.CSS_SELECTOR, ".pawn.piece"))
                        != nb_pawns
                    ):
                        done = True
                finally:
                    players_pos[idx] += 1

        evt = waitEvent(["start"])

        assert "max" in evt
        assert "min" in evt

        from itertools import count

        c = count()
        for n in range(int(47 / NB_PLAYERS) + 1):
            try:
                for i, drv in enumerate(self.drv):
                    if next(c) == 47:
                        raise EndOfGameError()
                    playerTurn(drv, i)
            except EndOfGameError as e:
                print("game end detected", e)
                sleep(1)
                makeShots(self.drv, "end_game")
                break

        if not ctx.endOfGame:
            waitEvent(["endOfGame"], maxTime=5)

        assert ctx.endOfGame is True, "Game didn't finish !!"

    def tearDown(self):
        if "WAIT" in os.environ:
            input("Press some key to continue...")
        for drv in self.drv:
            drv.close()


if __name__ == "__main__":
    unittest.main()
