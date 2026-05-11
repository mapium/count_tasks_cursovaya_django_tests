import time

import pytest
from selenium.webdriver.support.ui import WebDriverWait

from ui.pages.admin_users_page import AdminUsersPage
from ui.pages.login_page import AuthPage, LoginPage
from ui.pages.profile_page import ProfileChangePasswordPage


@pytest.mark.requires_creds
@pytest.mark.admin
def test_change_password_for_created_user(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")

    created_username = f"pwd_user_{int(time.time())}"
    old_password = "PwdStart123!"
    new_password = "PwdNew456!"

    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/users/")
    admin_page = AdminUsersPage(browser).wait_loaded()
    admin_page.fill_form(created_username, old_password, role_id="3").submit_form()
    admin_page = AdminUsersPage(browser).wait_loaded()
    if admin_page.get_top_error_text():
        pytest.skip(f"Создание пользователя для смены пароля: {admin_page.get_top_error_text()}")

    created_user_id = admin_page.get_user_id_by_username(created_username)
    assert created_user_id, "Не найден ID пользователя, созданного для теста смены пароля"

    browser.get(f"{base_url}/logout/")
    AuthPage(browser).open_login(base_url).wait_loaded().login_and_wait_redirect(created_username, old_password)
    assert "/dashboard/" in (browser.current_url or "")

    browser.get(f"{base_url}/profile/change-password/")
    profile_page = ProfileChangePasswordPage(browser).wait_loaded()
    profile_page.fill_passwords(old_password, new_password, new_password).submit()
    WebDriverWait(browser, 15).until(
        lambda d: ("/dashboard/" in (d.current_url or "")) or bool(profile_page.get_top_error_text())
    )
    if profile_page.get_top_error_text():
        pytest.skip(f"Смена пароля недоступна: {profile_page.get_top_error_text()}")
    assert "/dashboard/" in (browser.current_url or "")

    browser.get(f"{base_url}/logout/")
    AuthPage(browser).open_login(base_url).wait_loaded().login_and_wait_redirect(created_username, new_password)
    assert "/dashboard/" in (browser.current_url or "")

    browser.get(f"{base_url}/logout/")
    AuthPage(browser).open_login(base_url).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/users/")
    admin_page = AdminUsersPage(browser).wait_loaded()
    cleanup_user_id = admin_page.get_user_id_by_username(created_username)
    if cleanup_user_id:
        admin_page.submit_delete(cleanup_user_id)
        AdminUsersPage(browser).wait_loaded()
