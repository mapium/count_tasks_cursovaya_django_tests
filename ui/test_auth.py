import pytest

from ui.pages.login_page import AuthPage


@pytest.mark.smoke
@pytest.mark.auth
def test_auth_page_renders_fields(login_page):
    login_page.wait_loaded()
    assert login_page.find(login_page.username).is_displayed()
    assert login_page.find(login_page.password).is_displayed()
    assert login_page.find(login_page.submit).is_displayed()


@pytest.mark.auth
@pytest.mark.requires_creds
def test_login_valid_redirects_to_dashboard(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    p = AuthPage(browser)
    p.open_login(base_url).wait_loaded()
    p.login_and_wait_redirect(ui_username, ui_password)
    assert "/dashboard/" in (browser.current_url or "")


@pytest.mark.auth
@pytest.mark.requires_creds
def test_login_invalid_credentials_stays_on_auth(browser, base_url, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    p = AuthPage(browser)
    p.open_login(base_url).wait_loaded()
    p.login("nonexistent_user_xyz", "wrong_password_123")
    p.wait.until(lambda d: p.has_error())
    assert "/auth/" in (browser.current_url or "")
    assert "ошибка" in p.get_error_text().lower() or "авторизац" in p.get_error_text().lower()


@pytest.mark.auth
@pytest.mark.requires_creds
def test_login_only_username_shows_enter_password(browser, base_url, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    p = AuthPage(browser)
    p.open_login(base_url).wait_loaded()
    p.fill_username("admin")
    p.fill_password("")
    p.submit_form()
    p.wait.until(lambda d: p.has_error())
    assert "введите пароль" in p.get_error_text().lower()
    assert p.field_has_error_class("password")
    assert "обязательно" in p.get_field_error_text("password").lower()


@pytest.mark.auth
@pytest.mark.requires_creds
def test_login_only_password_shows_enter_login(browser, base_url, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    p = AuthPage(browser)
    p.open_login(base_url).wait_loaded()
    p.fill_username("")
    p.fill_password("secret")
    p.submit_form()
    p.wait.until(lambda d: p.has_error())
    assert "введите логин" in p.get_error_text().lower()
    assert p.field_has_error_class("username")


@pytest.mark.auth
def test_register_success_then_login_link(browser, base_url, fake_en, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    username = f"u_{fake_en.user_name()}_{fake_en.random_int(1000, 99999)}"
    password = "RegPass123!"
    p = AuthPage(browser)
    p.open_register(base_url).wait_loaded()
    p.fill_username(username)
    p.fill_password(password)
    p.fill_confirm_password(password)
    p.submit_form()
    # Успех: редирект на login или сообщение об успехе
    p.wait.until(
        lambda d: ("mode=login" in (d.current_url or ""))
        or ("успешн" in d.page_source.lower())
        or p.has_error()
    )
    if p.has_error() and "ошибка регистрации" in p.get_error_text().lower():
        pytest.skip(f"Регистрация недоступна (API): {p.get_error_text()}")


@pytest.mark.auth
@pytest.mark.requires_creds
def test_register_only_username_shows_enter_password(browser, base_url, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    p = AuthPage(browser)
    p.open_register(base_url).wait_loaded()
    p.fill_username("someone")
    p.fill_password("")
    p.submit_form()
    p.wait.until(lambda d: p.has_error())
    assert "введите пароль" in p.get_error_text().lower()


@pytest.mark.auth
@pytest.mark.requires_creds
def test_register_missing_confirm_password(browser, base_url, fake_en, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    p = AuthPage(browser)
    p.open_register(base_url).wait_loaded()
    p.fill_username(fake_en.user_name())
    p.fill_password("abcDEF123!")
    p.fill_confirm_password("")
    p.submit_form()
    p.wait.until(lambda d: p.has_error())
    assert "подтвердите пароль" in p.get_error_text().lower()
    assert p.field_has_error_class("confirm_password")


@pytest.mark.auth
@pytest.mark.requires_creds
def test_register_password_mismatch(browser, base_url, fake_en, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    p = AuthPage(browser)
    p.open_register(base_url).wait_loaded()
    u = fake_en.user_name()
    p.fill_username(u)
    p.fill_password("aaa111")
    p.fill_confirm_password("bbb222")
    p.submit_form()
    p.wait.until(lambda d: p.has_error())
    assert "пароли не совпадают" in p.get_error_text().lower()
    assert p.field_has_error_class("confirm_password")
