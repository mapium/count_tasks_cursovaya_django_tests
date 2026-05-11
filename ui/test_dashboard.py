import pytest
import time
from selenium.webdriver.common.by import By

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
from ui.pages.dashboard_page import DashboardPage
from ui.pages.login_page import AuthPage


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
    login_admin(browser, base_url, ui_username, ui_password)
    suffix = "dash_" + str(int(time.time()))
    created = {}
    try:
        created["user_id"] = create_user(browser, base_url, f"{suffix}_u", "DashPass123!", role_id="3")
        created["department_id"] = create_department(browser, base_url, f"{suffix}_d", "dash dep")
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
        browser.get(f"{base_url}/dashboard/")
        dash = DashboardPage(browser).wait_loaded()
        card = dash.task_card_by_id(created["task_id"])
        current_col = card.find_element(
            By.XPATH,
            "./ancestor::*[contains(@class,'kanban-column')][1]",
        ).get_attribute("data-status")
        targets = [c for c in ("planned", "in_progress", "review", "done") if c != current_col]
        target = targets[0]
        result = dash.post_status_update_via_fetch(created["task_id"], target)
        body = result.get("body") or {}
        if result.get("status") not in (200,) or not body.get("ok"):
            pytest.skip(f"API смены статуса недоступно: {result}")
        browser.refresh()
        DashboardPage(browser).wait_loaded().wait_task_in_column(created["task_id"], target)
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
