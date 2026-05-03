import os
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from tests.pages.login_page import AuthPage, LoginPage

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")


@pytest.fixture(scope="session")
def fake_ru() -> Faker:
    return Faker("ru_RU")


@pytest.fixture(scope="session")
def fake_en() -> Faker:
    return Faker()


@pytest.fixture(scope="session")
def chrome_options() -> Options:
    options = Options()

    if _env_bool("HEADLESS", default=True):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return options


@pytest.fixture
def browser(chrome_options: Options):
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()


@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, 30)


@pytest.fixture
def open_page(browser, base_url: str):
    def _open_page(path: str, page_class=None):
        url = f"{base_url}/{path.lstrip('/')}"
        browser.get(url)
        if page_class:
            return page_class(browser)
        return browser

    yield _open_page


@pytest.fixture
def login_page(browser, base_url: str) -> LoginPage:
    browser.get(f"{base_url}/auth/")
    return LoginPage(browser)


@pytest.fixture
def auth_page(browser, base_url: str) -> AuthPage:
    browser.get(f"{base_url}/auth/?mode=login")
    return AuthPage(browser)


@pytest.fixture
def logged_in_admin(browser, base_url: str, ui_username: str, ui_password: str):
    page = AuthPage(browser)
    page.open_login(base_url).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    yield browser


@pytest.fixture
def requests_session(logged_in_admin, base_url: str) -> requests.Session:
    """HTTP-сессия с cookies браузера после UI-логина администратора."""
    return session_from_driver(logged_in_admin, base_url)


def session_from_driver(driver, base_url: str) -> requests.Session:
    s = requests.Session()
    for c in driver.get_cookies():
        s.cookies.set(c["name"], c["value"])
    ua = driver.execute_script("return navigator.userAgent;") or "pytest-selenium"
    s.headers.update({"User-Agent": str(ua)})
    s.headers.update({"Referer": base_url.rstrip("/") + "/"})
    return s


@pytest.fixture(scope="session")
def ui_username() -> str | None:
    value = os.getenv("UI_USERNAME")
    return value.strip() if value else "admin"


@pytest.fixture(scope="session")
def ui_password() -> str | None:
    value = os.getenv("UI_PASSWORD")
    return value.strip() if value else "admin123"


@pytest.fixture(scope="session")
def run_creds_tests() -> bool:
    return _env_bool("RUN_CREDS_TESTS", default=True)
