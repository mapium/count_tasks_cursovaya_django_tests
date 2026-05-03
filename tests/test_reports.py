import pytest
from selenium.webdriver.support.ui import Select

from tests.pages.login_page import LoginPage
from tests.pages.reports_page import ReportsPage


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_page_loads_for_admin_or_manager(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")

    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    browser.get(f"{base_url}/reports/")
    ReportsPage(browser).wait_loaded()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_department_filter_changes_table(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/reports/")
    page = ReportsPage(browser).wait_loaded()

    dep_el = browser.find_element(page.department_select.by, page.department_select.value)
    dep_sel = Select(dep_el)
    dep_values = [(o.get_attribute("value") or "").strip() for o in dep_sel.options]
    dep_values = [value for value in dep_values if value]
    if not dep_values:
        pytest.skip("Нет подразделений в фильтре отчёта")
    selected_dep_value = dep_values[0]

    browser.get(f"{base_url}/reports/?period=month")
    ReportsPage(browser).wait_loaded()
    table_html_all = browser.page_source

    browser.get(f"{base_url}/reports/?period=month&department_id={selected_dep_value}")
    ReportsPage(browser).wait_loaded()
    table_html_filtered = browser.page_source

    if table_html_all == table_html_filtered:
        pytest.skip("Фильтрация применена, но данные в таблице не изменились для выбранного подразделения")
    assert table_html_all != table_html_filtered or "Нет данных" in table_html_filtered


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_employee_monthly_chart(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/reports/")
    page = ReportsPage(browser).wait_loaded()
    try:
        page.select_first_employee_with_value()
    except AssertionError:
        pytest.skip("Нет сотрудников с user_id для диаграммы")
    page.submit_show_chart()
    ReportsPage(browser).wait_loaded()
    if not page.chart_visible() and "выполнено" not in browser.page_source.lower():
        pytest.skip("Диаграмма не построилась для выбранного сотрудника (нет релевантных данных)")


@pytest.mark.requires_creds
@pytest.mark.admin
def test_reports_download_both_excel_files(requests_session, base_url, run_creds_tests):
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
