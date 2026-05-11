import re
import time

import pytest
from selenium.webdriver.common.by import By

from ui.pages.admin_departments_page import AdminDepartmentsPage
from ui.pages.login_page import LoginPage


def _extract_department_id(browser, name: str) -> str | None:
    # Ищем только в карточке отдела с точным заголовком:
    # regex по всей page_source давал ложные срабатывания после редактирования/удаления.
    sections = browser.find_elements(By.XPATH, f"//section[.//h3[normalize-space()='{name}']]")
    if not sections:
        return None
    section = sections[-1]
    dep_id_inputs = section.find_elements(By.XPATH, ".//input[@name='department_id']")
    if dep_id_inputs:
        value = (dep_id_inputs[0].get_attribute("value") or "").strip()
        return value or None
    tag = section.find_element(By.XPATH, ".//span[contains(@class,'tag')][contains(.,'ID')]")
    m2 = re.search(r"ID\s*(\d+)", tag.text)
    return m2.group(1) if m2 else None


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
    dep_id = None
    for _ in range(3):
        dep_id = _extract_department_id(browser, name)
        if dep_id:
            break
        browser.refresh()
        AdminDepartmentsPage(browser).wait_loaded()
        time.sleep(0.4)
    assert dep_id, "Не найден ID созданного подразделения"
    page.submit_delete(dep_id)
    AdminDepartmentsPage(browser).wait_loaded()
    assert _extract_department_id(browser, name) is None


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
    dep_id = None
    for _ in range(3):
        dep_id = _extract_department_id(browser, name)
        if dep_id:
            break
        browser.refresh()
        AdminDepartmentsPage(browser).wait_loaded()
        time.sleep(0.4)
    assert dep_id, "Не найден ID подразделения"

    page = AdminDepartmentsPage(browser)
    page.open_edit_for_department_id(dep_id)
    page.type(page.update_form_name(dep_id), name + " Изм")
    page.type(page.update_form_description(dep_id), "Новое описание после редактирования")
    page.submit_update(dep_id)
    AdminDepartmentsPage(browser).wait_loaded()
    assert "Изм" in browser.page_source or "Новое описание" in browser.page_source

    page = AdminDepartmentsPage(browser)
    deleted = False
    for _ in range(3):
        page.submit_delete(dep_id)
        AdminDepartmentsPage(browser).wait_loaded()
        if _extract_department_id(browser, name) is None and _extract_department_id(browser, name + " Изм") is None:
            deleted = True
            break
        browser.refresh()
        AdminDepartmentsPage(browser).wait_loaded()
    assert deleted, "Подразделение не удалилось после нескольких попыток"
