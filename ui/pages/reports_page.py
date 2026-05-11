from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from ui.pages.base_page import BasePage, Locator


class ReportsPage(BasePage):
    report_table = Locator(By.CSS_SELECTOR, ".reports-card table.table")
    department_select = Locator(By.CSS_SELECTOR, ".reports-card form.toolbar-row select[name='department_id']")
    period_select = Locator(By.CSS_SELECTOR, ".reports-card form.toolbar-row select[name='period']")
    show_tasks_btn = Locator(
        By.XPATH,
        "(//section[contains(@class,'reports-card')][not(contains(@class,'reports-card-side'))]"
        "//form[contains(@class,'toolbar-row')]//button[@type='submit' and contains(@class,'btn--primary')])[1]",
    )
    tasks_download_btn = Locator(
        By.CSS_SELECTOR,
        "button[name='action'][value='download_tasks_excel']",
    )
    employees_download_btn = Locator(
        By.CSS_SELECTOR,
        "button[name='action'][value='download_employees_excel']",
    )
    employee_chart_section = Locator(By.CSS_SELECTOR, "#employee-chart")
    employee_select = Locator(By.CSS_SELECTOR, "#employee-chart select[name='employee_id']")
    show_chart_btn = Locator(By.CSS_SELECTOR, "#employee-chart button[type='submit']")
    report_bars = Locator(By.CSS_SELECTOR, ".report-bars")

    def wait_loaded(self):
        self.wait.until(EC.presence_of_element_located((self.report_table.by, self.report_table.value)))
        return self

    def select_department_by_index(self, index: int):
        sel = Select(self.wait.until(EC.element_to_be_clickable((self.department_select.by, self.department_select.value))))
        sel.select_by_index(index)
        return self

    def select_department_by_value(self, value: str):
        sel = Select(self.find(self.department_select))
        sel.select_by_value(value)
        return self

    def submit_show_tasks(self):
        self.click(self.show_tasks_btn)
        return self

    def select_first_employee_with_value(self):
        sel = Select(self.wait.until(EC.presence_of_element_located((self.employee_select.by, self.employee_select.value))))
        for opt in sel.options:
            v = (opt.get_attribute("value") or "").strip()
            if v:
                sel.select_by_value(v)
                return v
        raise AssertionError("Нет сотрудников в списке отчёта")

    def submit_show_chart(self):
        self.click(self.show_chart_btn)
        return self

    def chart_visible(self) -> bool:
        return bool(self.finds(self.report_bars))
