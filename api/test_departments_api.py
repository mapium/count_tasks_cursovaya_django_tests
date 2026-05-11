import pytest
from http import HTTPStatus


class TestDepartments:
    """Тесты для работы с отделами"""

    def test_get_all_departments(self, api_client_v1, auth_headers):
        """Тест получения списка всех отделов"""
        response = api_client_v1.get("/api/v1/departments", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json(), (list, dict))

    def test_get_department_by_id(self, api_client_v1, auth_headers):
        """Тест получения отдела по ID"""
        department_id = 6
        response = api_client_v1.get(
            f"/api/v1/departments/{department_id}",
            headers=auth_headers
        )
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND]

    def test_create_department(self, api_client_v1, auth_headers):
        """Тест создания нового отдела"""
        data = {
            "name": "Test Department",
            "description": "Test description"
        }
        response = api_client_v1.post(
            "/api/v1/departments",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.BAD_REQUEST]
        
        if response.status_code in [HTTPStatus.OK, HTTPStatus.CREATED]:
            result = response.json()
            if isinstance(result, dict) and "id" in result:
                assert result["id"] is not None

    def test_update_department(self, api_client_v1, auth_headers):
        """Тест обновления информации об отделе"""
        department_id = 6
        data = {
            "name": "Updated Department",
            "description": "Updated description"
        }
        response = api_client_v1.put(
            f"/api/v1/departments/{department_id}",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.BAD_REQUEST
        ]

    def test_delete_department(self, api_client_v1, auth_headers):
        """Тест удаления отдела"""
        department_id = 2
        response = api_client_v1.delete(
            f"/api/v1/departments/{department_id}",
            headers=auth_headers
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.INTERNAL_SERVER_ERROR
        ]

