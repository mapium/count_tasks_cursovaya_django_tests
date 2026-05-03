from datetime import date, timedelta

import pytest
from selenium.webdriver.support.ui import Select

from tests.pages.login_page import LoginPage
from tests.pages.task_create_page import TaskCreatePage


def _select_coherent_assignment(page: TaskCreatePage):
    """Подбирает согласованную связку creator/department/assignee для API.

    Предпочитает менеджера (role_id=2), чтобы department_id был однозначен.
    """
    creator_el = page.find(page.creator_select)
    creator_sel = Select(creator_el)
    assignee_sel = Select(page.find(page.assignee_select))
    department_el = page.find(page.department_select)
    department_sel = Select(department_el) if department_el.is_enabled() else None

    creator_candidates = []
    for opt in creator_sel.options:
        value = (opt.get_attribute("value") or "").strip()
        if not value:
            continue
        creator_candidates.append(
            {
                "value": value,
                "role_id": (opt.get_attribute("data-role-id") or "").strip(),
                "dep_id": (opt.get_attribute("data-department-id") or "").strip(),
            }
        )
    if not creator_candidates:
        raise AssertionError("Нет доступных creator в форме")

    # Сначала пробуем менеджеров с department_id, затем остальных.
    creator_candidates.sort(key=lambda item: 0 if item["role_id"] == "2" and item["dep_id"] else 1)

    last_error = None
    for candidate in creator_candidates:
        creator_sel.select_by_value(candidate["value"])
        dep_id = candidate["dep_id"]

        # При явном департаменте подставляем его в селект (если он доступен).
        if dep_id and department_sel is not None:
            try:
                department_sel.select_by_value(dep_id)
            except Exception:
                pass

        # Ищем исполнителя из того же департамента, если dep_id известен.
        chosen_assignee = None
        for aopt in assignee_sel.options:
            aval = (aopt.get_attribute("value") or "").strip()
            if not aval:
                continue
            adep = (aopt.get_attribute("data-department-id") or "").strip()
            if dep_id and adep and adep != dep_id:
                continue
            chosen_assignee = aval
            break

        if not chosen_assignee:
            last_error = f"для creator={candidate['value']} не найден подходящий assignee"
            continue

        assignee_sel.select_by_value(chosen_assignee)
        return

    raise AssertionError(last_error or "Не удалось подобрать согласованную связку creator/assignee")


@pytest.mark.requires_creds
@pytest.mark.admin
def test_create_task_via_ui(browser, base_url, ui_username, ui_password, fake_ru, run_creds_tests):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    browser.get(f"{base_url}/task_create/")
    page = TaskCreatePage(browser).wait_loaded()

    title = f"Автотест задача {fake_ru.word()}"
    page.type(page.title, title)
    page.type(page.description, fake_ru.sentence())

    page.set_select_value(page.status, "planned")
    page.set_select_value(page.priority, "малый")

    start = date.today()
    end = start + timedelta(days=7)
    page.set_date_value(page.start_date, start.isoformat())
    page.set_date_value(page.end_date, end.isoformat())

    if not page.has_select_options(page.assignee_select):
        pytest.skip("Нет исполнителей (API/токен)")
    try:
        _select_coherent_assignment(page)
    except AssertionError as exc:
        pytest.skip(f"Невозможно подобрать creator/assignee: {exc}")

    page.force_submit_form()
    top_error = page.get_top_error_text()
    if top_error:
        pytest.fail(
            "Не удалось создать задачу через UI.\n"
            f"Сообщение страницы: {top_error}\n"
            "Проверьте данные справочников (создатель/исполнитель/подразделение) и права пользователя."
        )

    page.wait_success()


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
    ui_username,
    ui_password,
    fake_ru,
    run_creds_tests,
    missing_field,
    expected_top_error_substr,
    expected_field_error_substr,
):
    if not run_creds_tests:
        pytest.skip("RUN_CREDS_TESTS=0")
    browser.get(f"{base_url}/auth/")
    LoginPage(browser).wait_loaded().login_and_wait_redirect(ui_username, ui_password)

    browser.get(f"{base_url}/task_create/")
    page = TaskCreatePage(browser).wait_loaded()

    if not page.has_select_options(page.assignee_select):
        pytest.skip("Нет исполнителей (API/токен)")

    creator_el = page.find(page.creator_select)
    if missing_field == "creator_id" and not creator_el.is_enabled():
        pytest.skip("Поле создателя недоступно (не admin)")

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

    if creator_el.is_enabled():
        if missing_field != "creator_id":
            page.select_first_non_empty(page.creator_select)

    department_el = page.find(page.department_select)
    if department_el.is_enabled():
        page.select_first_non_empty(page.department_select)

    if missing_field != "assignee_id":
        page.select_first_non_empty(page.assignee_select)

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
