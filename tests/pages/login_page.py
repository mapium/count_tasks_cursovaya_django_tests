from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.pages.base_page import BasePage, Locator


class AuthPage(BasePage):
    username = Locator(By.CSS_SELECTOR, "form.auth-form input[name='username']")
    password = Locator(By.CSS_SELECTOR, "form.auth-form input[name='password']")
    confirm_password = Locator(By.CSS_SELECTOR, "form.auth-form input[name='confirm_password']")
    submit = Locator(By.CSS_SELECTOR, "form.auth-form button[type='submit']")
    error_alert = Locator(By.CSS_SELECTOR, ".auth-error[role='alert']")
    register_tab = Locator(By.CSS_SELECTOR, "a.btn[href*='mode=register']")
    login_tab = Locator(By.CSS_SELECTOR, "a.btn[href*='mode=login']")

    def open_login(self, base_url: str):
        self.driver.get(f"{base_url.rstrip('/')}/auth/?mode=login")
        return self

    def open_register(self, base_url: str):
        self.driver.get(f"{base_url.rstrip('/')}/auth/?mode=register")
        return self

    def fill_username(self, text: str):
        self.type(self.username, text)
        return self

    def fill_password(self, text: str):
        el = self.wait.until(EC.visibility_of_element_located((self.password.by, self.password.value)))
        el.clear()
        if text:
            el.send_keys(text)
        return self

    def fill_confirm_password(self, text: str):
        el = self.wait.until(EC.visibility_of_element_located((self.confirm_password.by, self.confirm_password.value)))
        el.clear()
        if text:
            el.send_keys(text)
        return self

    def submit_form(self):
        self.click(self.submit)
        return self

    def login(self, username: str, password: str):
        self.fill_username(username)
        self.fill_password(password)
        self.submit_form()
        return self

    def login_and_wait_redirect(self, username: str, password: str):
        self.login(username, password)
        self.wait.until(lambda d: "/auth/" not in (d.current_url or ""))
        return self

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located((self.submit.by, self.submit.value)))
        return self

    def get_error_text(self) -> str:
        errors = self.finds(self.error_alert)
        if not errors:
            return ""
        return errors[0].text.strip()

    def has_error(self) -> bool:
        return bool(self.finds(self.error_alert))

    def get_field_error_text(self, field_name: str) -> str:
        xpath = (
            f"//form[contains(@class,'auth-form')]"
            f"//label[contains(@class,'field')][.//*[@name='{field_name}']]"
            f"//small[contains(@class,'field-error')]"
        )
        els = self.driver.find_elements(By.XPATH, xpath)
        return els[0].text.strip() if els else ""

    def field_has_error_class(self, field_name: str) -> bool:
        sel = f"form.auth-form input[name='{field_name}'].input--error"
        return bool(self.driver.find_elements(By.CSS_SELECTOR, sel))


# Обратная совместимость с существующими тестами
LoginPage = AuthPage
