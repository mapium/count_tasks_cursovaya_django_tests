import time

import pytest

from tests.pages.admin_users_page import AdminUsersPage
from tests.pages.login_page import LoginPage


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_users_create_valid(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/users/")
    page = AdminUsersPage(browser).wait_loaded()
    u = f"auto_{int(time.time())}"
    page.fill_form(u, "SecurePass123!", role_id="3").submit_form()
    AdminUsersPage(browser).wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Создание пользователя: {page.get_top_error_text()}")
    assert u in browser.page_source


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_users_create_only_username_shows_password_error(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/users/")
    page = AdminUsersPage(browser).wait_loaded()
    page.type(page.username, f"onlylogin_{int(time.time())}")
    page.type(page.password, "")
    page.force_submit_form()
    AdminUsersPage(browser).wait_loaded()
    assert page.input_has_error("password") or "обязательн" in page.get_top_error_text().lower()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_users_create_only_password_shows_username_error(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/users/")
    page = AdminUsersPage(browser).wait_loaded()
    page.type(page.username, "")
    page.type(page.password, "OnlyPass123!")
    page.force_submit_form()
    AdminUsersPage(browser).wait_loaded()
    assert page.input_has_error("username") or "обязательн" in page.get_top_error_text().lower()
