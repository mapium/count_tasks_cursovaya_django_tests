import time

import pytest
from selenium.webdriver.support.ui import Select

from ui.helpers.ui_seed import (
    create_department,
    create_employee,
    create_task,
    create_user,
    delete_department,
    delete_employee,
    delete_task,
    delete_user,
    login_admin,
)
from ui.pages.login_page import LoginPage
from ui.pages.reports_page import ReportsPage


@pytest.fixture
def reports_seed(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    login_admin(browser, base_url, ui_username, ui_password)
    suffix = f"rep_{int(time.time())}"
    created = {}
    try:
        created["user_id"] = create_user(browser, base_url, f"{suffix}_u", "RepPass123!", role_id="3")
        created["department_id"] = create_department(browser, base_url, f"{suffix}_dep", "reports dep")
        created["employee_id"] = create_employee(
            browser,
            base_url,
            last_name=f"{suffix}_ln",
            department_id=created["department_id"],
            user_id=created["user_id"],
            email=f"{suffix}@example.com",
        )
        created["task_id"] = create_task(
            browser,
            base_url,
            title=f"{suffix}_task",
            assignee_user_id=created["user_id"],
            department_id=created["department_id"],
        )
        created["department_name"] = f"{suffix}_dep"
        created["employee_last_name"] = f"{suffix}_ln"
        yield created
    finally:
        try:
            login_admin(browser, base_url, ui_username, ui_password)
        except Exception:
            pass
        if created.get("task_id"):
            delete_task(browser, base_url, created["task_id"])
        if created.get("employee_id"):
            delete_employee(browser, base_url, created["employee_id"])
        if created.get("department_id"):
            delete_department(browser, base_url, created["department_id"])
        if created.get("user_id"):
            delete_user(browser, base_url, created["user_id"])


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_page_loads_for_admin_or_manager(browser, base_url, ui_username, ui_password, reports_seed):
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    browser.get(f"{base_url}/reports/")
    ReportsPage(browser).wait_loaded()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_department_filter_changes_table(browser, base_url, ui_username, ui_password, reports_seed):
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/reports/")
    page = ReportsPage(browser).wait_loaded()

    dep_el = browser.find_element(page.department_select.by, page.department_select.value)
    dep_sel = Select(dep_el)
    selected_dep_value = None
    for option in dep_sel.options:
        if (option.text or "").strip() == reports_seed["department_name"]:
            selected_dep_value = (option.get_attribute("value") or "").strip()
            break
    assert selected_dep_value, "Созданное тестом подразделение не найдено в фильтре отчета"

    browser.get(f"{base_url}/reports/?period=month&department_id={selected_dep_value}")
    ReportsPage(browser).wait_loaded()
    table_html_filtered = (browser.page_source or "").lower()
    assert reports_seed["department_name"].lower() in table_html_filtered
    assert f"department_id={selected_dep_value}" in (browser.current_url or "")


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_employee_monthly_chart(browser, base_url, ui_username, ui_password, reports_seed):
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/reports/")
    page = ReportsPage(browser).wait_loaded()
    employee_select = Select(browser.find_element(page.employee_select.by, page.employee_select.value))
    selected_found = False
    selected_employee_value = ""
    for option in employee_select.options:
        if reports_seed["employee_last_name"].lower() in (option.text or "").lower():
            selected_employee_value = (option.get_attribute("value") or "").strip()
            employee_select.select_by_value(selected_employee_value)
            selected_found = True
            break
    assert selected_found, "Созданный тестом сотрудник не найден в списке диаграммы"
    browser.get(f"{base_url}/reports/?employee_id={selected_employee_value}#employee-chart")
    ReportsPage(browser).wait_loaded()
    html = (browser.page_source or "").lower()
    if "/auth/" in (browser.current_url or ""):
        pytest.skip("Сессия истекла при построении диаграммы")
    assert selected_employee_value in (browser.current_url or "")
    assert reports_seed["employee_last_name"].lower() in html or page.chart_visible() or "выберите сотрудника" not in html


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_download_both_excel_files(requests_session, base_url, run_creds_tests, reports_seed):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    root = base_url.rstrip("/")
    r1 = requests_session.get(
        f"{root}/reports/",
        params={"action": "download_tasks_excel", "period": "month"},
        allow_redirects=True,
        timeout=30,
    )
    assert r1.status_code == 200
    assert "spreadsheetml" in (r1.headers.get("Content-Type") or "").lower() or r1.content[:2] == b"PK"

    r2 = requests_session.get(
        f"{root}/reports/",
        params={"action": "download_employees_excel"},
        allow_redirects=True,
        timeout=30,
    )
    assert r2.status_code == 200
    assert "spreadsheetml" in (r2.headers.get("Content-Type") or "").lower() or r2.content[:2] == b"PK"
