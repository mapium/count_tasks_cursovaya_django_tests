from datetime import date, timedelta
import time

import pytest
from selenium.webdriver.support.ui import Select

from ui.pages.login_page import LoginPage
from ui.pages.task_create_page import TaskCreatePage
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


@pytest.fixture
def isolated_task_context(browser, base_url, ui_username, ui_password, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    login_admin(browser, base_url, ui_username, ui_password)
    suffix = int(time.time())
    username = f"task_user_{suffix}"
    department_name = f"task_dep_{suffix}"
    last_name = f"TaskLn{suffix}"
    created = {}
    try:
        created["user_id"] = create_user(browser, base_url, username, "TaskPass123!", role_id="3")
        created["department_id"] = create_department(browser, base_url, department_name, "task dep")
        created["employee_id"] = create_employee(
            browser,
            base_url,
            last_name=last_name,
            department_id=created["department_id"],
            user_id=created["user_id"],
            email=f"{username}@example.com",
        )
        yield created
    finally:
        try:
            login_admin(browser, base_url, ui_username, ui_password)
        except Exception:
            return
        if created.get("employee_id"):
            delete_employee(browser, base_url, created["employee_id"])
        if created.get("department_id"):
            delete_department(browser, base_url, created["department_id"])
        if created.get("user_id"):
            delete_user(browser, base_url, created["user_id"])


@pytest.mark.requires_creds
@pytest.mark.admin
def test_create_task_via_ui(browser, base_url, fake_ru, isolated_task_context):
    page = TaskCreatePage(browser)
    title = f"ui_task_{int(time.time())}_{fake_ru.word()}"
    task_id = None
    try:
        task_id = create_task(
            browser,
            base_url,
            title=title,
            assignee_user_id=isolated_task_context["user_id"],
            department_id=isolated_task_context["department_id"],
        )
        assert task_id
    finally:
        if task_id:
            delete_task(browser, base_url, task_id)


@pytest.mark.requires_creds
@pytest.mark.admin
@pytest.mark.parametrize(
    "missing_field,expected_top_error_substr,expected_field_error_substr",
    [
        ("title", "Укажите название задачи", "Поле обязательно"),
        ("description", "Укажите описание задачи", "Поле обязательно"),
        ("priority", "Укажите приоритет задачи", "Поле обязательно"),
        ("status", "Укажите статус задачи", "Поле обязательно"),
        ("assignee_id", "Выберите исполнителя задачи", "Поле обязательно"),
        ("start_date", "Укажите дату начала", "Поле обязательно"),
        ("end_date", "Укажите дату окончания", "Поле обязательно"),
        ("creator_id", "Выберите создателя задачи", "Поле обязательно"),
    ],
)
def test_task_create_form_shows_error_for_each_required_field(
    browser,
    base_url,
    fake_ru,
    missing_field,
    expected_top_error_substr,
    expected_field_error_substr,
    isolated_task_context,
):
    browser.get(f"{base_url}/task_create/")
    page = TaskCreatePage(browser).wait_loaded()

    start = date.today()
    end = start + timedelta(days=7)

    valid = {
        "title": f"Автотест задача {fake_ru.word()}",
        "description": fake_ru.sentence(),
        "priority": "малый",
        "status": "planned",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }

    page.type(page.title, valid["title"])
    page.type(page.description, valid["description"])
    page.set_select_value(page.priority, valid["priority"])
    page.set_select_value(page.status, valid["status"])
    page.set_date_value(page.start_date, valid["start_date"])
    page.set_date_value(page.end_date, valid["end_date"])
    if missing_field != "creator_id":
        page.select_first_non_empty(page.creator_select)
    page.set_select_raw_value(page.department_select, str(isolated_task_context["department_id"]))
    if missing_field != "assignee_id":
        Select(page.find(page.assignee_select)).select_by_value(str(isolated_task_context["user_id"]))

    if missing_field == "title":
        page.type(page.title, "")
    elif missing_field == "description":
        page.type(page.description, "")
    elif missing_field == "priority":
        page.set_select_value(page.priority, "")
    elif missing_field == "status":
        page.set_select_value(page.status, "")
    elif missing_field == "start_date":
        page.set_date_value(page.start_date, "")
    elif missing_field == "end_date":
        page.set_date_value(page.end_date, "")
    elif missing_field == "assignee_id":
        Select(page.find(page.assignee_select)).select_by_value("")
    elif missing_field == "creator_id":
        Select(page.find(page.creator_select)).select_by_value("")

    page.force_submit_form()
    page.wait_any_error()

    assert expected_top_error_substr.lower() in page.get_top_error_text().lower()
    assert expected_field_error_substr.lower() in page.get_field_error_text(missing_field).lower()
