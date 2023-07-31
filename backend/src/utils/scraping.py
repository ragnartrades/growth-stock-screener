from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from typing import Callable, List
from aiohttp.client import ClientSession
from utils.logging import skip_message
from lxml import html
import re


async def get(url: str, session: ClientSession) -> str:
    """Send a GET request for the given url and return the response as a string."""
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception:
        return None


def extract_element(xpath: str, response: str) -> WebElement:
    """Return the WebElement at a given xpath from a GET request response."""
    if response is None:
        return None

    dom = html.fromstring(response)

    try:
        element = dom.xpath(xpath)[0]
        return element
    except Exception:
        return None


def extract_float(element: WebElement) -> float:
    """Return the content stored in a WebElement as a float."""
    try:
        cleaned_content = re.sub(r"[^0-9.]", "", element.text)
        return float(cleaned_content)
    except Exception:
        return None


def element_is_float(xpath: str) -> Callable[[WebDriver], bool]:
    """Return a function which consumes a WebDriver and returns true if the DOM element
    at the specified xpath is a float type."""

    def inner(driver: WebDriver) -> bool:
        return type(extract_float(driver.find_element(By.XPATH, xpath))) == float

    return inner


class WaitForAll:
    """Expected condition which is the logical "and" of multiple expected conditions."""

    def __init__(self, methods: List[Callable[[WebDriver], bool]]):
        self.methods = methods

    def __call__(self, driver: WebDriver) -> bool:
        try:
            for method in self.methods:
                if not method(driver):
                    return False
            return True
        except StaleElementReferenceException:
            return False
