from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from ui.pages.base_page import BasePage, Locator


class TaskCreatePage(BasePage):
    title = Locator(By.CSS_SELECTOR, "form.form-grid input[name='title']")
    creator_select = Locator(By.ID, "creatorSelect")
    assignee_select = Locator(By.ID, "assigneeSelect")
    department_select = Locator(By.ID, "departmentSelect")
    status = Locator(By.CSS_SELECTOR, "form.form-grid select[name='status']")
    priority = Locator(By.CSS_SELECTOR, "form.form-grid select[name='priority']")
    start_date = Locator(By.CSS_SELECTOR, "form.form-grid input[name='start_date']")
    end_date = Locator(By.CSS_SELECTOR, "form.form-grid input[name='end_date']")
    description = Locator(By.CSS_SELECTOR, "form.form-grid textarea[name='description']")
    submit_btn = Locator(By.CSS_SELECTOR, "form.form-grid button[type='submit']")
    success_message = Locator(By.CSS_SELECTOR, "section.card p[style*='color: var(--success)']")
    top_error = Locator(By.CSS_SELECTOR, "section.card p.auth-error")

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located((self.title.by, self.title.value)))
        return self

    def set_select_value(self, locator: Locator, value: str):
        Select(self.find(locator)).select_by_value(value)
        return self

    def set_select_raw_value(self, locator: Locator, value: str):
        el = self.find(locator)
        self.driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            el,
            value,
        )
        return self

    def set_select_index(self, locator: Locator, index: int):
        Select(self.find(locator)).select_by_index(index)
        return self

    def has_select_options(self, locator: Locator) -> bool:
        select = Select(self.find(locator))
        return any(o.get_attribute("value") for o in select.options)

    def select_first_non_empty(self, locator: Locator):
        sel = Select(self.find(locator))
        for opt in sel.options:
            value = (opt.get_attribute("value") or "").strip()
            if value:
                sel.select_by_value(value)
                return self
        raise AssertionError("No non-empty options in select")

    def submit(self):
        self.click(self.submit_btn)
        return self

    def set_date_value(self, locator: Locator, iso_date: str):
        el = self.find(locator)
        self.driver.execute_script(
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            el,
            iso_date,
        )
        return self

    def force_submit_form(self):
        return self.force_submit("form.form-grid")

    def wait_success(self):
        self.wait.until(
            EC.visibility_of_element_located((self.success_message.by, self.success_message.value))
        )
        return self

    def get_field_error_text(self, field_name: str) -> str:
        xpath = (
            f"//form[contains(@class,'form-grid')]"
            f"//label[contains(@class,'field')][.//*[@name='{field_name}']]"
            f"//small[contains(@class,'field-error')]"
        )
        els = self.driver.find_elements(By.XPATH, xpath)
        return els[0].text.strip() if els else ""

    def get_top_error_text(self) -> str:
        els = self.finds(self.top_error)
        return els[0].text.strip() if els else ""

    def wait_any_error(self):
        self.wait.until(
            lambda d: (
                len(d.find_elements(By.CSS_SELECTOR, "section.card p.auth-error")) > 0
                or len(d.find_elements(By.CSS_SELECTOR, "small.field-error")) > 0
            )
        )
        return self

