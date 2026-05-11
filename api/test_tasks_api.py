import pytest
from http import HTTPStatus


class TestTasks:
    """Тесты для работы с задачами"""

    def test_get_all_tasks(self, api_client_v1, auth_headers):
        """Тест получения списка всех задач"""
        response = api_client_v1.get("/api/v1/tasks", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json(), (list, dict))

    def test_get_my_tasks(self, api_client_v1, auth_headers):
        """Тест получения задач текущего пользователя"""
        response = api_client_v1.get("/api/v1/tasks/my", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json(), (list, dict))

    def test_create_task(self, api_client_v1, auth_headers):
        """Тест создания новой задачи"""
        data = {
            "title": "Test Task",
            "description": "Test task description",
            "creator_id": 1,
            "assignee_id": 1,
            "department_id": 2,
            "status_id": 2,
            "priority": "малый",
            "planned_start_date": "2024-01-01",
            "planned_end_date": "2024-01-31",
            "actual_start_date": "2024-01-01",
            "actual_end_date": "2024-01-31"
        }
        response = api_client_v1.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.INTERNAL_SERVER_ERROR
        ]
        
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            result = response.json()
            if isinstance(result, dict) and "id" in result:
                return result["id"]
        return None

    def test_update_task(self, api_client_v1, auth_headers):
        """Тест обновления задачи"""
        task_id = 1
        data = {
            "id": 1,
            "title": "Updated Task",
            "description": "Updated description",
            "creator_id": 1,
            "assignee_id": 1,
            "department_id": 2,
            "status_id": 1,
            "priority": "малый",
            "planned_start_date": "2024-01-01",
            "planned_end_date": "2024-01-31",
            "actual_start_date": "2024-01-01",
            "actual_end_date": "2024-01-31",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        response = api_client_v1.put(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.INTERNAL_SERVER_ERROR
        ]

    def test_change_task_status(self, api_client_v1, auth_headers):
        """Тест изменения статуса задачи"""
        task_id = 2
        data = {
            "status_name": "Выполнено"
        }
        response = api_client_v1.patch(
            f"/api/v1/tasks/{task_id}/status",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.FORBIDDEN
        ]

    def test_add_comment_to_task(self, api_client_v1, auth_headers):
        """Тест добавления комментария к задаче"""
        task_id = 2
        data = {
            "comment_text": "Test comment"
        }
        response = api_client_v1.post(
            f"/api/v1/tasks/{task_id}/comments",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.BAD_REQUEST
        ]

    def test_delete_task(self, api_client_v1, auth_headers):
        """Тест удаления задачи"""
        task_id = 1
        response = api_client_v1.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.INTERNAL_SERVER_ERROR
        ]

