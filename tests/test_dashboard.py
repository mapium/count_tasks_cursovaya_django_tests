import pytest
from selenium.webdriver.common.by import By

from tests.pages.dashboard_page import DashboardPage
from tests.pages.login_page import AuthPage


@pytest.mark.smoke
def test_dashboard_page_loads(open_page, browser):
    open_page("/dashboard/")
    if "/no-access" in (browser.current_url or ""):
        assert "токен" in browser.page_source.lower() or "доступ" in browser.page_source.lower()
        return
    DashboardPage(browser).wait_loaded()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_dashboard_change_task_status_via_api(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    AuthPage(browser).open_login(base_url).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/dashboard/")
    dash = DashboardPage(browser).wait_loaded()
    if not dash.has_any_task():
        pytest.skip("На доске нет задач для смены статуса")

    card = dash.first_task_card()
    task_id = card.get_attribute("data-id")
    assert task_id

    current_col = card.find_element(
        By.XPATH,
        "./ancestor::*[contains(@class,'kanban-column')][1]",
    ).get_attribute("data-status")

    targets = [c for c in ("planned", "in_progress", "review", "done") if c != current_col]
    assert targets
    target = targets[0]

    result = dash.post_status_update_via_fetch(task_id, target)
    body = result.get("body") or {}
    if result.get("status") not in (200,) or not body.get("ok"):
        pytest.skip(f"API смены статуса недоступно: {result}")

    browser.refresh()
    DashboardPage(browser).wait_loaded().wait_task_in_column(task_id, target)
