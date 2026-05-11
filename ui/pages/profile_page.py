from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ui.pages.base_page import BasePage, Locator


class ProfileChangePasswordPage(BasePage):
    old_password = Locator(By.CSS_SELECTOR, "form.form-grid input[name='old_password']")
    new_password = Locator(By.CSS_SELECTOR, "form.form-grid input[name='new_password']")
    confirm_password = Locator(By.CSS_SELECTOR, "form.form-grid input[name='confirm_password']")
    submit_btn = Locator(By.CSS_SELECTOR, "form.form-grid button[type='submit']")
    top_error = Locator(By.CSS_SELECTOR, "section.card p.auth-error")

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located((self.submit_btn.by, self.submit_btn.value)))
        return self

    def fill_passwords(self, old_password: str, new_password: str, confirm_password: str):
        self.type(self.old_password, old_password)
        self.type(self.new_password, new_password)
        self.type(self.confirm_password, confirm_password)
        return self

    def submit(self):
        self.click(self.submit_btn)
        return self

    def get_top_error_text(self) -> str:
        els = self.finds(self.top_error)
        return els[0].text.strip() if els else ""
