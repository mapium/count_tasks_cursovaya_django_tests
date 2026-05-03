import json
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from tests.pages.base_page import BasePage, Locator


class DashboardPage(BasePage):
    kanban_board = Locator(By.ID, "kanbanBoard")
    stats_grid = Locator(By.CSS_SELECTOR, ".stats-grid")
    any_task_card = Locator(By.CSS_SELECTOR, "#kanbanBoard .task-card")
    export_excel_link = Locator(By.XPATH, "//a[contains(., 'Экспорт в Excel')]")

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located((self.kanban_board.by, self.kanban_board.value)))
        self.wait.until(EC.visibility_of_element_located((self.stats_grid.by, self.stats_grid.value)))
        return self

    def has_any_task(self) -> bool:
        return len(self.finds(self.any_task_card)) > 0

    def first_task_card(self):
        cards = self.finds(self.any_task_card)
        return cards[0] if cards else None

    def task_card_by_id(self, task_id: int | str):
        return self.driver.find_element(
            By.CSS_SELECTOR,
            f"#kanbanBoard .task-card[data-id='{task_id}']",
        )

    def column_tasks_container(self, status: str):
        """status: planned | in_progress | review | done"""
        return self.driver.find_element(
            By.CSS_SELECTOR,
            f"#kanbanBoard .kanban-column[data-status='{status}'] .kanban-tasks",
        )

    def post_status_update_via_fetch(self, task_id: int | str, target_column: str) -> dict:
        """Тот же POST, что и в static/js/kanban.js (устойчивее HTML5 DnD в Selenium)."""
        script = """
        var callback = arguments[arguments.length - 1];
        var taskId = arguments[0];
        var col = arguments[1];
        var url = window.DASHBOARD_STATUS_UPDATE_URL;
        if (!url) { callback(JSON.stringify({ok:false, error:'no url'})); return; }
        var input = document.querySelector("input[name='csrfmiddlewaretoken']");
        var csrf = input ? input.value : "";
        var body = new URLSearchParams();
        body.set("task_id", String(taskId));
        body.set("target_column", col);
        fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "X-CSRFToken": csrf
          },
          body: body.toString()
        }).then(function(r) { return r.json().then(function(j) { return {status: r.status, body: j}; }); })
        .then(function(x) { callback(JSON.stringify(x)); })
        .catch(function(e) { callback(JSON.stringify({status: 0, body: {ok:false, error: String(e)}})); });
        """
        raw = self.driver.execute_async_script(script, str(task_id), target_column)
        data = json.loads(raw) if isinstance(raw, str) else raw
        return data

    def drag_task_to_column(self, task_id: int | str, target_column: str) -> None:
        """HTML5 drag-and-drop (может быть нестабилен в CI; тесты могут использовать post_status_update_via_fetch)."""
        card = self.task_card_by_id(task_id)
        target = self.column_tasks_container(target_column)
        ActionChains(self.driver).click_and_hold(card).pause(0.25).move_to_element(target).pause(0.25).release().perform()
        time.sleep(0.4)

    def wait_task_in_column(self, task_id: int | str, target_column: str):
        sel = f"#kanbanBoard .kanban-column[data-status='{target_column}'] .task-card[data-id='{task_id}']"
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
        return self
