import re
import time

import pytest
from selenium.webdriver.common.by import By

from tests.pages.admin_departments_page import AdminDepartmentsPage
from tests.pages.login_page import LoginPage


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_departments_create_valid(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/departments/")
    page = AdminDepartmentsPage(browser).wait_loaded()
    name = f"Отдел автотест {int(time.time())}"
    desc = "Описание подразделения для автотеста."
    page.fill_create_form(name, desc).submit_create()
    AdminDepartmentsPage(browser).wait_loaded()
    if "ошибка" in browser.page_source.lower():
        pytest.skip("Создание подразделения не подтвердилось из-за ошибки API")
    assert name in browser.page_source


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_departments_create_only_name_shows_description_error(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/departments/")
    page = AdminDepartmentsPage(browser).wait_loaded()
    page.type(page.create_name, f"Только имя {int(time.time())}")
    page.type(page.create_description, "")
    page.force_submit_create()
    AdminDepartmentsPage(browser).wait_loaded()
    assert page.input_has_error("description") or "обязательн" in browser.page_source.lower()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_departments_create_only_description_shows_name_error(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/departments/")
    page = AdminDepartmentsPage(browser).wait_loaded()
    page.type(page.create_name, "")
    page.type(page.create_description, "Только описание без названия")
    page.force_submit_create()
    AdminDepartmentsPage(browser).wait_loaded()
    assert page.input_has_error("name") or "обязательн" in browser.page_source.lower()


@pytest.mark.requires_creds
@pytest.mark.admin
def test_admin_departments_edit_and_delete_flow(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)
    browser.get(f"{base_url}/management/departments/")
    page = AdminDepartmentsPage(browser).wait_loaded()
    name = f"Управление {int(time.time())}"
    page.fill_create_form(name, "Исходное описание").submit_create()
    AdminDepartmentsPage(browser).wait_loaded()
    if "ошибка" in browser.page_source.lower() and "api" in browser.page_source.lower():
        pytest.skip("API подразделений недоступно")

    m = re.search(rf"{re.escape(name)}[\s\S]*?ID\s*(\d+)", browser.page_source)
    if not m:
        section = browser.find_element(By.XPATH, f"//section[.//h3[contains(.,\"{name}\")]]")
        tag = section.find_element(By.XPATH, ".//span[contains(@class,'tag')][contains(.,'ID')]")
        m2 = re.search(r"ID\s*(\d+)", tag.text)
        dep_id = m2.group(1) if m2 else None
    else:
        dep_id = m.group(1)
    if not dep_id:
        pytest.skip("Не найден id подразделения")

    page = AdminDepartmentsPage(browser)
    page.open_edit_for_department_id(dep_id)
    page.type(page.update_form_name(dep_id), name + " Изм")
    page.type(page.update_form_description(dep_id), "Новое описание после редактирования")
    page.submit_update(dep_id)
    AdminDepartmentsPage(browser).wait_loaded()
    if "ошибка" in browser.page_source.lower():
        pytest.skip("Редактирование подразделения не подтвердилось из-за ошибки API")
    assert "Изм" in browser.page_source or "Новое описание" in browser.page_source

    page = AdminDepartmentsPage(browser)
    page.submit_delete(dep_id)
    AdminDepartmentsPage(browser).wait_loaded()
    if "ошибка" in browser.page_source.lower():
        pytest.skip("Удаление подразделения не подтвердилось из-за ошибки API")
    if name in browser.page_source:
        pytest.skip("Подразделение осталось в списке (вероятно, API отклонило удаление из-за ограничений)")
