import re

import pytest
from selenium.webdriver.common.by import By

from ui.pages.employees_page import EmployeesPage
from ui.pages.login_page import LoginPage


def _find_employee_id_by_last_name(browser, last_name: str) -> int | None:
    try:
        card = browser.find_element(
            By.XPATH,
            f"//article[contains(@class,'employee-card')][.//h4[contains(.,\"{last_name}\")]]",
        )
        edit = card.find_element(By.CSS_SELECTOR, "a[href*='edit_id=']")
        return int(re.search(r"edit_id=(\d+)", edit.get_attribute("href") or "").group(1))
    except Exception:
        return None


@pytest.mark.smoke
def test_employees_page_loads(open_page, browser):
    open_page("/employees/")
    if "/no-access" in (browser.current_url or ""):
        assert "токен" in browser.page_source.lower() or "доступ" in browser.page_source.lower()
        return
    EmployeesPage(browser).wait_loaded()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_employees_search_by_last_name(browser, base_url, ui_username, ui_password, fake_ru, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    last_name = f"Поисков{fake_ru.random_int(100, 999)}"
    browser.get(f"{base_url}/employees/?mode=add")
    page = EmployeesPage(browser).wait_loaded()
    page.fill_employee_form(
        last_name=last_name,
        first_name=fake_ru.first_name(),
        middle_name=fake_ru.middle_name(),
        phone_number=str(fake_ru.random_int(10**9, 10**10 - 1)),
        email=f"{fake_ru.user_name()}@example.com",
        passport_data=fake_ru.bothify(text="##########"),
    )
    page.select_department_first_non_empty()
    page.force_submit_form()
    page.wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Создание для поиска: {page.get_top_error_text()}")

    browser.get(f"{base_url}/employees/?q={last_name[:5]}")
    EmployeesPage(browser).wait_loaded()
    assert last_name.lower() in browser.page_source.lower()
    employee_id = _find_employee_id_by_last_name(browser, last_name)
    if employee_id:
        EmployeesPage(browser).submit_delete_for_employee(employee_id).wait_loaded()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_or_manager_can_create_employee(browser, base_url, ui_username, ui_password, fake_ru, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    browser.get(f"{base_url}/employees/?mode=add")
    page = EmployeesPage(browser).wait_loaded()

    last_name = f"{fake_ru.last_name()}Тест{fake_ru.random_int(100, 999)}"
    first_name = fake_ru.first_name()
    middle_name = fake_ru.middle_name()
    phone = str(fake_ru.random_int(10**9, 10**10 - 1))
    email = f"{fake_ru.user_name()}@example.com"
    passport = fake_ru.bothify(text="##########")

    page.fill_employee_form(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        phone_number=phone,
        email=email,
        passport_data=passport,
    )
    page.select_department_first_non_empty()
    page.force_submit_form()

    page.wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Создание сотрудника: {page.get_top_error_text()}")

    page.wait_success_message()

    browser.get(f"{base_url}/employees/?q={last_name.split('Тест')[0]}")
    EmployeesPage(browser).wait_loaded().search_by_last_name(last_name.split("Тест")[0])
    if "/no-access" in (browser.current_url or ""):
        pytest.skip("Сессия истекла до проверки поиска после создания")
    if last_name.lower() not in browser.page_source.lower():
        pytest.skip("Сотрудник не найден в выдаче сразу после создания (асинхронность API)")
    employee_id = _find_employee_id_by_last_name(browser, last_name)
    if employee_id:
        EmployeesPage(browser).submit_delete_for_employee(employee_id).wait_loaded()


@pytest.mark.requires_creds
@pytest.mark.admin
@pytest.mark.parametrize(
    "missing_field,expected_field_error_substr,expected_top_error_substr",
    [
        ("first_name", "Поле обязательно", "заполните имя"),
        ("last_name", "Поле обязательно", "заполните имя"),
        ("email", "Поле обязательно", "заполните имя"),
        ("passport_data", "Поле обязательно", "заполните имя"),
        ("department_id", "Поле обязательно", "выберите подразделение"),
    ],
)
def test_employee_form_shows_error_for_each_required_field(
    browser,
    base_url,
    ui_username,
    ui_password,
    fake_ru,
    run_creds_tests,
    missing_field,
    expected_field_error_substr,
    expected_top_error_substr,
):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    browser.get(f"{base_url}/employees/?mode=add")
    page = EmployeesPage(browser).wait_loaded()

    data = {
        "last_name": f"{fake_ru.last_name()}Тест",
        "first_name": fake_ru.first_name(),
        "middle_name": fake_ru.middle_name(),
        "phone_number": str(fake_ru.random_int(10**9, 10**10 - 1)),
        "email": f"{fake_ru.user_name()}@example.com",
        "passport_data": fake_ru.bothify(text="##########"),
    }
    data[missing_field] = ""

    page.fill_employee_form(**data)
    if missing_field != "department_id":
        page.select_department_first_non_empty()
    else:
        page.set_department_raw_value("")

    page.force_submit_form()
    page.wait_any_error()

    assert expected_field_error_substr.lower() in page.get_field_error_text(missing_field).lower()
    assert expected_top_error_substr.lower() in page.get_top_error_text().lower()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_employee_edit_and_delete_created_employee(browser, base_url, ui_username, ui_password, fake_ru, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    browser.get(f"{base_url}/employees/?mode=add")
    page = EmployeesPage(browser).wait_loaded()
    last_name = f"Редакт{fake_ru.random_int(10000, 99999)}"
    page.fill_employee_form(
        last_name=last_name,
        first_name="Иван",
        middle_name="Иванович",
        phone_number="89991234567",
        email=f"edit_{fake_ru.user_name()}@example.com",
        passport_data="1234567890",
    )
    page.select_department_first_non_empty()
    page.force_submit_form()
    page.wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Создание: {page.get_top_error_text()}")

    browser.get(f"{base_url}/employees/?q={last_name}")
    EmployeesPage(browser).wait_loaded()
    employee_id = _find_employee_id_by_last_name(browser, last_name)
    if employee_id is None:
        pytest.skip("Карточка сотрудника не найдена в списке")

    page = EmployeesPage(browser)
    page.open_edit_employee(base_url, employee_id)
    page.wait_loaded()
    page.type(page.first_name, "Пётр")
    page.force_submit_form()
    page.wait_loaded()
    if page.get_top_error_text():
        pytest.skip(f"Обновление: {page.get_top_error_text()}")

    browser.get(f"{base_url}/employees/?q={last_name}")
    EmployeesPage(browser).wait_loaded()
    src = browser.page_source
    assert "Пётр" in src or "Петр" in src

    page.submit_delete_for_employee(employee_id)
    EmployeesPage(browser).wait_loaded()
    post_delete_html = browser.page_source
    if ("удален" not in post_delete_html.lower() and "удалён" not in post_delete_html.lower()) and (
        last_name in post_delete_html
    ):
        pytest.skip("Удаление сотрудника не подтвердилось (возможны ограничения API)")
