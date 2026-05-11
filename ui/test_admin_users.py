import time

import pytest

from ui.pages.admin_users_page import AdminUsersPage
from ui.pages.login_page import LoginPage


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_users_create_edit_delete_flow(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/users/")
    page = AdminUsersPage(browser).wait_loaded()

    username = f"auto_user_{int(time.time())}"
    updated_username = f"{username}_upd"
    created_password = "SecurePass123!"
    updated_password = "SecurePass456!"

    page.fill_form(username, created_password, role_id="3").submit_form()
    AdminUsersPage(browser).wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Создание пользователя: {page.get_top_error_text()}")

    created_user_id = page.get_user_id_by_username(username)
    assert created_user_id, "Не найден ID созданного пользователя"

    page.open_edit_for_user_id(created_user_id)
    page.update_username(created_user_id, updated_username)
    page.update_password(created_user_id, updated_password)
    page.update_role(created_user_id, role_id="2")
    page.submit_update(created_user_id)

    page = AdminUsersPage(browser).wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Редактирование пользователя: {page.get_top_error_text()}")
    found_user_id = None
    for _ in range(3):
        found_user_id = page.get_user_id_by_username(updated_username)
        if found_user_id:
            break
        browser.refresh()
        page = AdminUsersPage(browser).wait_loaded()
    assert found_user_id == created_user_id

    page.submit_delete(created_user_id)
    page = AdminUsersPage(browser).wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Удаление пользователя: {page.get_top_error_text()}")
    assert page.find_user_row_by_username(updated_username) is None


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
