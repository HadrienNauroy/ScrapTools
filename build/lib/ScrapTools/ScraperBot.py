"""A file to define A scraping bot class """

# selenium imports
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains as A
from selenium.webdriver.common.keys import Keys as K
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# other imports
import speech_recognition as sr
import os
import tempfile
import time as tm
import requests
import subprocess
import logging as lg

# local imports
from ScrapTools.Decorators import retry, ToManyTry


# suppression des affichages de webdriver-manager
os.environ["WDM_LOG_LEVEL"] = "0"
os.environ["WDM_PRINT_FIRST_LINE"] = "False"

lg.basicConfig(level=lg.ERROR)


class DownloadFailed(Exception):
    pass


class RequestError(Exception):
    pass


class ScraperBot:
    def __init__(self, headless=False, timeout=5):
        """
        Function to initialise a selenium webdriver with all necessary parameters
        We use Chromedriver
        """

        # scraping with selenium
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        if headless:
            options.add_argument("headless")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.action = A(self.driver)
        # used in wait for element
        self.timeout = timeout

    def wait_for_elem(self, locator_type, locator):
        """
        Simple wrapper around selenium's find_element
        -- added a simple mechanism to wait until the element we want is present.
        Use try/except with `selenium.common.exceptions.TimeoutException`
        """
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((locator_type, locator))
        )

    def is_elem_present(self, locator_type, locator):
        """
        Check if an element is present or wait for a timeout.
        Return the element if present otherwise False
        """
        try:
            return self.wait_for_elem(locator_type, locator)
        except TimeoutException:
            return False

    def solve_captha(self, frame):

        """
        A function aimed to solve a captcha

        frame: the frame on wich the catpha is located

        sucess: a boolean

        Based on https://github.com/threadexio/python-captcha-bypass
        """

        # switch to captcha button frame
        self.driver.switch_to.frame(frame)
        self.wait_for_elem(By.CLASS_NAME, "recaptcha-checkbox-border").click()
        # switch to captcha challenge frame
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(
            self.wait_for_elem(By.XPATH, "/html/body/div[3]/div[4]/iframe")
        )
        # select audio challenge
        self.wait_for_elem(By.ID, "recaptcha-audio-button").click()

        # go to audio challenge frame and get download link
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(
            self.wait_for_elem(By.XPATH, "/html/body/div[3]/div[4]/iframe")
        )
        download_link = self.wait_for_elem(
            By.CLASS_NAME, "rc-audiochallenge-tdownload-link"
        )

        # set usefull file for solving the captcha
        tmp_dir = tempfile.gettempdir()
        mp3_file = os.path.join(tmp_dir, "_tmp.mp3")
        wav_file = os.path.join(tmp_dir, "_tmp.wav")
        tmp_files = [mp3_file, wav_file]

        # download audio
        tm.sleep(2)
        with open("_tmp.mp3", "wb") as f:
            link = download_link.get_attribute("href")
            try:
                r = _rget(link, allow_redirect=True)
            except Exception as e:
                print(e)
                raise DownloadFailed("Could download audio file")
            f.write(r.content)
            f.close()

        # Convert to wav
        subprocess.call(
            [
                "C:/ffmpeg/bin/ffmpeg.exe",
                "-i",
                "_tmp.mp3",
                "_tmp.wav",
            ]
        )

        # Using google's own api against them
        recognizer = sr.Recognizer()

        with sr.AudioFile("_tmp.wav") as source:
            recorded_audio = recognizer.listen(source)
            text = recognizer.recognize_google(recorded_audio, show_all=True)
            print(f"{text} \n\n\n\n")

        # Type out the answer
        self.wait_for_elem(By.ID, "audio-response").send_keys(text)

        # Click the "Verify" button to complete
        self.wait_for_elem(By.ID, "recaptcha-verify-button").click()

        # remove temporary files
        _cleanup(tmp_files)

    def kill(self):
        self.driver.close()


@retry
def _rget(link, **kwargs):
    """
    Simple wraper around request.get function to raise Error if request failed
    """
    r = requests.get(link, kwargs)
    if r.status_code != 200:
        raise RequestError(f"[{r.status_code}]")
    return r


def _cleanup(files: list):
    for x in files:
        if os.path.exists(x):
            os.remove(x)


if __name__ == "__main__":
    _rget("https://github.com/threadexio/python-captcha-bypass")
