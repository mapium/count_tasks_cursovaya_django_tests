from __future__ import annotations

from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@dataclass(frozen=True)
class Locator:
    by: By
    value: str


class BasePage:
    def __init__(self, driver: WebDriver, timeout_s: int = 20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout_s)

    def find(self, locator: Locator):
        return self.driver.find_element(locator.by, locator.value)

    def finds(self, locator: Locator):
        return self.driver.find_elements(locator.by, locator.value)

    def click(self, locator: Locator):
        self.wait.until(EC.element_to_be_clickable((locator.by, locator.value))).click()
        return self

    def type(self, locator: Locator, text: str, clear: bool = True):
        el = self.wait.until(EC.visibility_of_element_located((locator.by, locator.value)))
        if clear:
            el.clear()
        el.send_keys(text)
        return self

    def force_submit(self, form_css: str):
        """
        Bypass HTML5 constraint validation (required/minlength) by calling form.submit().
        This is necessary because our Django views render server-side field errors.
        """
        form = self.driver.find_element(By.CSS_SELECTOR, form_css)
        self.driver.execute_script("arguments[0].submit();", form)
        return self

    def select_has_option(self, select_locator: Locator) -> bool:
        el = self.wait.until(EC.presence_of_element_located((select_locator.by, select_locator.value)))
        options = el.find_elements(By.CSS_SELECTOR, "option")
        return any(opt.get_attribute("value") for opt in options)

    def current_path(self) -> str:
        # Works for local dev base_url as well.
        return self.driver.current_url.split("://", 1)[-1].split("/", 1)[-1]

