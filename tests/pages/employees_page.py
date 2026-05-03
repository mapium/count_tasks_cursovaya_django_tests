from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from tests.pages.base_page import BasePage, Locator


class EmployeesPage(BasePage):
    search_input = Locator(By.CSS_SELECTOR, "form.toolbar-row input[name='q']")
    filter_submit = Locator(By.CSS_SELECTOR, "form.toolbar-row button[type='submit']")
    add_employee_link = Locator(By.CSS_SELECTOR, "form.toolbar-row a.btn.btn--primary")

    # Form fields (when mode=add/edit)
    last_name = Locator(By.CSS_SELECTOR, "form.modal-dialog__body input[name='last_name']")
    first_name = Locator(By.CSS_SELECTOR, "form.modal-dialog__body input[name='first_name']")
    middle_name = Locator(By.CSS_SELECTOR, "form.modal-dialog__body input[name='middle_name']")
    phone_number = Locator(By.CSS_SELECTOR, "form.modal-dialog__body input[name='phone_number']")
    email = Locator(By.CSS_SELECTOR, "form.modal-dialog__body input[name='email']")
    passport_data = Locator(By.CSS_SELECTOR, "form.modal-dialog__body input[name='passport_data']")
    department_id = Locator(By.CSS_SELECTOR, "form.modal-dialog__body select[name='department_id']")
    is_active = Locator(By.CSS_SELECTOR, "form.modal-dialog__body input[name='is_active']")
    submit_btn = Locator(By.CSS_SELECTOR, "form.modal-dialog__body button[type='submit']")

    toast_success = Locator(By.CSS_SELECTOR, "section.card p[style*='color: var(--success)']")
    top_error = Locator(By.CSS_SELECTOR, "section.card p.auth-error")

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located((self.search_input.by, self.search_input.value)))
        return self

    def search_by_last_name(self, q: str):
        self.type(self.search_input, q)
        self.click(self.filter_submit)
        return self

    def open_add_form(self):
        self.click(self.add_employee_link)
        return self

    def select_department_first_non_empty(self):
        sel = Select(self.wait.until(EC.presence_of_element_located((self.department_id.by, self.department_id.value))))
        for opt in sel.options:
            v = (opt.get_attribute("value") or "").strip()
            if v:
                sel.select_by_value(v)
                return self
        return self

    def set_department_raw_value(self, value: str):
        el = self.find(self.department_id)
        self.driver.execute_script(
            "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            el,
            value,
        )
        return self

    def open_edit_employee(self, base_url: str, employee_id: int):
        self.driver.get(f"{base_url.rstrip('/')}/employees/?mode=edit&edit_id={employee_id}")
        return self

    def submit_delete_for_employee(self, employee_id: int):
        xpath = (
            f"//form[.//input[@name='employee_id' and @value='{employee_id}']]"
            f"//button[@type='submit' and contains(@class,'btn--danger')]"
        )
        btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        btn.click()
        return self

    def input_has_error(self, field_name: str) -> bool:
        sel = f"form.modal-dialog__body input[name='{field_name}'].input--error, form.modal-dialog__body select[name='{field_name}'].input--error"
        return bool(self.driver.find_elements(By.CSS_SELECTOR, sel))

    def fill_employee_form(
        self,
        *,
        last_name: str,
        first_name: str,
        middle_name: str,
        phone_number: str,
        email: str,
        passport_data: str,
        department_id: str | None = None,
    ):
        self.type(self.last_name, last_name)
        self.type(self.first_name, first_name)
        self.type(self.middle_name, middle_name)
        self.type(self.phone_number, phone_number)
        self.type(self.email, email)
        self.type(self.passport_data, passport_data)
        if department_id is not None:
            self.set_department_raw_value(department_id)
        return self

    def submit(self):
        self.click(self.submit_btn)
        return self

    def force_submit_form(self):
        return self.force_submit("form.modal-dialog__body")

    def wait_success_message(self):
        self.wait.until(EC.visibility_of_element_located((self.toast_success.by, self.toast_success.value)))
        return self

    def get_field_error_text(self, field_name: str) -> str:
        # template: <label class="field"> ... <input name="..."> ... <small class="field-error">TEXT</small>
        xpath = (
            f"//form[contains(@class,'modal-dialog__body')]"
            f"//label[contains(@class,'field')][.//*[@name='{field_name}']]"
            f"//small[contains(@class,'field-error')]"
        )
        els = self.driver.find_elements(By.XPATH, xpath)
        return els[0].text.strip() if els else ""

    def get_top_error_text(self) -> str:
        els = self.finds(self.top_error)
        return els[0].text.strip() if els else ""

    def wait_any_error(self):
        # wait until either top error or any field-error appears
        self.wait.until(
            lambda d: (
                len(d.find_elements(By.CSS_SELECTOR, "section.card p.auth-error")) > 0
                or len(d.find_elements(By.CSS_SELECTOR, "small.field-error")) > 0
            )
        )
        return self

