from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from ui.pages.base_page import BasePage, Locator


class AdminUsersPage(BasePage):
    username = Locator(By.CSS_SELECTOR, "form.toolbar-row input[name='username']")
    password = Locator(By.CSS_SELECTOR, "form.toolbar-row input[name='password']")
    role_select = Locator(By.CSS_SELECTOR, "form.toolbar-row select[name='role_id']")
    submit = Locator(By.CSS_SELECTOR, "form.toolbar-row button[type='submit']")
    users_table = Locator(By.CSS_SELECTOR, "div.table-wrap table.table")

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located((self.username.by, self.username.value)))
        return self

    def fill_form(self, username: str, password: str, role_id: str = "3"):
        self.type(self.username, username)
        self.type(self.password, password)
        Select(self.find(self.role_select)).select_by_value(role_id)
        return self

    def submit_form(self):
        self.click(self.submit)
        return self

    def force_submit_form(self):
        return self.force_submit("form.toolbar-row")

    def input_has_error(self, field_name: str) -> bool:
        return bool(
            self.driver.find_elements(
                By.CSS_SELECTOR,
                f"form.toolbar-row input[name='{field_name}'].input--error",
            )
        )

    def get_field_error_text(self, field_name: str) -> str:
        if field_name == "username" and self.input_has_error("username"):
            els = self.driver.find_elements(By.CSS_SELECTOR, "form.toolbar-row ~ small.field-error")
            return els[0].text.strip() if els else ""
        if field_name == "password" and self.input_has_error("password"):
            els = self.driver.find_elements(By.CSS_SELECTOR, "form.toolbar-row ~ small.field-error")
            if not els:
                return ""
            if self.input_has_error("username") and len(els) > 1:
                return els[1].text.strip()
            return els[0].text.strip()
        return ""

    def get_top_error_text(self) -> str:
        els = self.driver.find_elements(By.CSS_SELECTOR, "section.card p.auth-error")
        return els[0].text.strip() if els else ""

    def get_success_text(self) -> str:
        els = self.driver.find_elements(By.CSS_SELECTOR, "section.card p.muted[style*='var(--success)']")
        return els[0].text.strip() if els else ""

    def find_user_row_by_username(self, username: str):
        xpath = (
            "//table[contains(@class,'table--admin-users')]//tr"
            f"[td[2][normalize-space()='{username}']]"
        )
        rows = self.driver.find_elements(By.XPATH, xpath)
        return rows[0] if rows else None

    def get_user_id_by_username(self, username: str) -> str | None:
        row = self.find_user_row_by_username(username)
        if not row:
            return None
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells:
            return None
        value = (cells[0].text or "").strip()
        return value or None

    def open_edit_for_user_id(self, user_id: str | int):
        btn = self.driver.find_element(
            By.CSS_SELECTOR,
            f"button.js-toggle-user-edit[data-target-id='user-edit-{user_id}']",
        )
        btn.click()
        return self

    def update_username(self, user_id: str | int, username: str):
        self.type(Locator(By.CSS_SELECTOR, f"form#user-edit-{user_id} input[name='username']"), username)
        return self

    def update_password(self, user_id: str | int, password: str):
        self.type(Locator(By.CSS_SELECTOR, f"form#user-edit-{user_id} input[name='password']"), password)
        return self

    def update_role(self, user_id: str | int, role_id: str = "3"):
        Select(self.find(Locator(By.CSS_SELECTOR, f"form#user-edit-{user_id} select[name='role_id']"))).select_by_value(
            role_id
        )
        return self

    def submit_update(self, user_id: str | int):
        self.click(Locator(By.CSS_SELECTOR, f"form#user-edit-{user_id} button[type='submit']"))
        return self

    def submit_delete(self, user_id: str | int):
        form_xpath = (
            f"//form[.//input[@name='action' and @value='user_delete']]"
            f"[.//input[@name='user_id' and @value='{user_id}']]"
        )
        form = self.driver.find_element(By.XPATH, form_xpath)
        self.driver.execute_script("arguments[0].submit();", form)
        return self
