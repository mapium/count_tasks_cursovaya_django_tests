from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from ui.pages.base_page import BasePage, Locator


class AdminDepartmentsPage(BasePage):
    create_name = Locator(By.CSS_SELECTOR, "form.form-grid input[name='name']")
    create_description = Locator(By.CSS_SELECTOR, "form.form-grid textarea[name='description']")
    create_submit = Locator(
        By.XPATH,
        "//section[contains(@class,'card')][.//h3[contains(.,'Создать подразделение')]]//form//button[@type='submit']",
    )
    top_error = Locator(By.CSS_SELECTOR, "section.card p.auth-error")

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located((self.create_name.by, self.create_name.value)))
        return self

    def fill_create_form(self, name: str, description: str):
        self.type(self.create_name, name)
        self.type(self.create_description, description)
        return self

    def submit_create(self):
        self.click(self.create_submit)
        return self

    def force_submit_create(self):
        form = self.driver.find_element(
            By.XPATH,
            "//form[.//input[@name='action' and @value='department_create']]",
        )
        self.driver.execute_script("arguments[0].submit();", form)
        return self

    def get_field_error_text(self, field_name: str) -> str:
        xpath = (
            f"//form[.//input[@name='action' and @value='department_create']]"
            f"//label[contains(@class,'field')][.//*[@name='{field_name}']]"
            f"//small[contains(@class,'field-error')]"
        )
        els = self.driver.find_elements(By.XPATH, xpath)
        return els[0].text.strip() if els else ""

    def input_has_error(self, field_name: str) -> bool:
        sel = f"form.form-grid input[name='{field_name}'].input--error, form.form-grid textarea[name='{field_name}'].input--error"
        return bool(self.driver.find_elements(By.CSS_SELECTOR, sel))

    def open_edit_for_department_id(self, dep_id: int | str):
        btn = self.driver.find_element(
            By.CSS_SELECTOR,
            f"button.js-toggle-department-edit[data-target-id='dep-edit-{dep_id}']",
        )
        btn.click()
        return self

    def update_form_name(self, dep_id: int | str):
        return Locator(By.CSS_SELECTOR, f"form#dep-edit-{dep_id} input[name='name']")

    def update_form_description(self, dep_id: int | str):
        return Locator(By.CSS_SELECTOR, f"form#dep-edit-{dep_id} textarea[name='description']")

    def submit_update(self, dep_id: int | str):
        form = self.driver.find_element(By.CSS_SELECTOR, f"form#dep-edit-{dep_id}")
        form.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        return self

    def submit_delete(self, dep_id: int | str):
        form_xpath = (
            f"//form[.//input[@name='action' and @value='department_delete']]"
            f"[.//input[@name='department_id' and @value='{dep_id}']]"
        )
        last_error = None
        for _ in range(3):
            try:
                form = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, form_xpath))
                )
                self.driver.execute_script("arguments[0].submit();", form)
                return self
            except (StaleElementReferenceException, TimeoutException) as exc:
                last_error = exc
        if last_error:
            raise last_error
        return self
