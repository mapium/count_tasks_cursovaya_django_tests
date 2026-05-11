import re
import time
from datetime import date, timedelta

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

from ui.pages.admin_departments_page import AdminDepartmentsPage
from ui.pages.admin_users_page import AdminUsersPage
from ui.pages.employees_page import EmployeesPage
from ui.pages.login_page import LoginPage
from ui.pages.task_create_page import TaskCreatePage


def _open_with_retry(browser, url: str, attempts: int = 3):
    last_error = None
    for _ in range(attempts):
        try:
            browser.get(url)
            return
        except (TimeoutException, WebDriverException) as exc:
            last_error = exc
            time.sleep(0.6)
    if last_error:
        raise last_error


def login_admin(browser, base_url: str, ui_username: str, ui_password: str):
    last_error = None
    for _ in range(3):
        try:
            _open_with_retry(browser, f"{base_url}/auth/")
            LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
            return
        except (TimeoutException, WebDriverException) as exc:
            last_error = exc
            time.sleep(0.7)
    if last_error:
        raise last_error


def create_user(browser, base_url: str, username: str, password: str, role_id: str = "3") -> str:
    _open_with_retry(browser, f"{base_url}/management/users/")
    page = AdminUsersPage(browser).wait_loaded()
    page.fill_form(username, password, role_id=role_id).submit_form()
    page = AdminUsersPage(browser).wait_loaded()
    if page.get_top_error_text():
        raise AssertionError(page.get_top_error_text())
    wait = WebDriverWait(browser, 8)
    wait.until(lambda d: page.get_user_id_by_username(username) is not None or bool(page.get_top_error_text()))
    user_id = page.get_user_id_by_username(username)
    if user_id:
        return user_id
    for _ in range(3):
        _open_with_retry(browser, f"{base_url}/management/users/")
        page = AdminUsersPage(browser).wait_loaded()
        user_id = page.get_user_id_by_username(username)
        if user_id:
            return user_id
        time.sleep(0.4)
    raise AssertionError("Не найден ID созданного пользователя")


def delete_user(browser, base_url: str, user_id: str):
    for _ in range(3):
        try:
            _open_with_retry(browser, f"{base_url}/management/users/")
            page = AdminUsersPage(browser).wait_loaded()
            page.submit_delete(user_id)
            AdminUsersPage(browser).wait_loaded()
            return
        except Exception:
            time.sleep(0.5)


def create_department(browser, base_url: str, name: str, description: str) -> str:
    _open_with_retry(browser, f"{base_url}/management/departments/")
    page = AdminDepartmentsPage(browser).wait_loaded()
    page.fill_create_form(name, description).submit_create()
    page = AdminDepartmentsPage(browser).wait_loaded()
    if "ошибка api" in browser.page_source.lower():
        raise AssertionError("Ошибка API при создании подразделения")
    dep_id = None
    for _ in range(4):
        sections = browser.find_elements(By.XPATH, f"//section[.//h3[normalize-space()='{name}']]")
        if sections:
            section = sections[-1]
            dep_id_input = section.find_element(By.XPATH, ".//input[@name='department_id']")
            dep_id = (dep_id_input.get_attribute("value") or "").strip()
            if dep_id:
                return dep_id
        _open_with_retry(browser, f"{base_url}/management/departments/")
        AdminDepartmentsPage(browser).wait_loaded()
        time.sleep(0.4)
    raise AssertionError("Не найдено созданное подразделение по имени")


def delete_department(browser, base_url: str, department_id: str):
    for _ in range(3):
        try:
            _open_with_retry(browser, f"{base_url}/management/departments/")
            page = AdminDepartmentsPage(browser).wait_loaded()
            page.submit_delete(department_id)
            AdminDepartmentsPage(browser).wait_loaded()
            return
        except Exception:
            time.sleep(0.5)


def create_employee(
    browser,
    base_url: str,
    last_name: str,
    department_id: str,
    user_id: str,
    email: str,
) -> int:
    _open_with_retry(browser, f"{base_url}/employees/?mode=add")
    page = EmployeesPage(browser).wait_loaded()
    page.fill_employee_form(
        last_name=last_name,
        first_name="Auto",
        middle_name="Seed",
        phone_number="89990001122",
        email=email,
        passport_data="1234567890",
    )
    Select(page.find(page.department_id)).select_by_value(str(department_id))
    Select(page.find(page.user_id)).select_by_value(str(user_id))
    page.force_submit_form()
    page.wait_loaded()
    if page.get_top_error_text():
        raise AssertionError(page.get_top_error_text())

    _open_with_retry(browser, f"{base_url}/employees/?q={last_name}")
    EmployeesPage(browser).wait_loaded()
    card = browser.find_element(
        By.XPATH,
        f"//article[contains(@class,'employee-card')][.//h4[contains(.,\"{last_name}\")]]",
    )
    edit = card.find_element(By.CSS_SELECTOR, "a[href*='edit_id=']")
    match = re.search(r"edit_id=(\d+)", edit.get_attribute("href") or "")
    if not match:
        raise AssertionError("Не найден ID созданного сотрудника")
    return int(match.group(1))


def delete_employee(browser, base_url: str, employee_id: int):
    for _ in range(3):
        try:
            _open_with_retry(browser, f"{base_url}/employees/")
            page = EmployeesPage(browser).wait_loaded()
            page.submit_delete_for_employee(employee_id)
            EmployeesPage(browser).wait_loaded()
            return
        except Exception:
            time.sleep(0.5)


def create_task(browser, base_url: str, title: str, assignee_user_id: str, department_id: str) -> int:
    _open_with_retry(browser, f"{base_url}/task_create/")
    page = TaskCreatePage(browser).wait_loaded()
    page.type(page.title, title)
    page.type(page.description, "Task created by isolated UI test flow")
    page.set_select_value(page.status, "planned")
    page.set_select_value(page.priority, "средний")
    today = date.today()
    page.set_date_value(page.start_date, today.isoformat())
    page.set_date_value(page.end_date, (today + timedelta(days=3)).isoformat())
    creator_select = Select(page.find(page.creator_select))
    creator_chosen = False
    for option in creator_select.options:
        value = (option.get_attribute("value") or "").strip()
        role_id = (option.get_attribute("data-role-id") or "").strip()
        if value and role_id == "1":
            creator_select.select_by_value(value)
            creator_chosen = True
            break
    if not creator_chosen:
        page.select_first_non_empty(page.creator_select)
    Select(page.find(page.assignee_select)).select_by_value(str(assignee_user_id))
    page.set_select_raw_value(page.department_select, str(department_id))
    page.force_submit_form()
    page.wait_loaded()
    if page.get_top_error_text():
        raise AssertionError(page.get_top_error_text())

    _open_with_retry(browser, f"{base_url}/dashboard/")
    link = browser.find_element(
        By.XPATH,
        f"//a[contains(@class,'task-title-link') and normalize-space()=\"{title}\"]",
    )
    href = link.get_attribute("href") or ""
    match = re.search(r"/dashboard/tasks/(\d+)/", href)
    if not match:
        raise AssertionError("Не найден ID созданной задачи")
    return int(match.group(1))


def delete_task(browser, base_url: str, task_id: int):
    for _ in range(3):
        try:
            _open_with_retry(browser, f"{base_url}/dashboard/tasks/{task_id}/")
            form = browser.find_element(By.XPATH, "//form[.//input[@name='action' and @value='delete']]")
            browser.execute_script("arguments[0].submit();", form)
            return
        except Exception:
            time.sleep(0.5)
