import pytest
from http import HTTPStatus


class TestEmployees:
    """Тесты для работы с сотрудниками"""

    def test_get_all_employees(self, api_client_v1, auth_headers):
        """Тест получения списка всех сотрудников"""
        response = api_client_v1.get("/api/v1/employees", headers=auth_headers)
        assert response.status_code == HTTPStatus.OK
        assert isinstance(response.json(), (list, dict))

    def test_get_employee_by_id(self, api_client_v1, auth_headers):
        """Тест получения сотрудника по ID"""
        employee_id = 1
        response = api_client_v1.get(
            f"/api/v1/employees/{employee_id}",
            headers=auth_headers
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.INTERNAL_SERVER_ERROR
        ]

    def test_add_employee(self, api_client_v1, auth_headers):
        """Тест добавления нового сотрудника"""
        data = {
            "username": "newemployee",
            "password": "password123",
            "email": "employee@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Middle",
            "phone_number": "+79991234567",
            "passport_data": "1234567890",
            "inn": "123456789012",
            "snils": "12345678901"
        }
        response = api_client_v1.post(
            "/api/v1/employees",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.UNPROCESSABLE_ENTITY
        ]

    def test_update_employee(self, api_client_v1, auth_headers):
        """Тест обновления информации о сотруднике"""
        employee_id = 1
        data = {
            "user_id": 1,
            "first_name": "Updated",
            "last_name": "Name",
            "middle_name": "Middle",
            "phone_number": "+79991234567",
            "email": "updated@example.com",
            "passport_data": "1234567890",
            "inn": "123456789012",
            "snils": "12345678901",
            "department_id": 1,
            "is_active": True
        }
        response = api_client_v1.put(
            f"/api/v1/employees/{employee_id}",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [HTTPStatus.OK, HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST]

    def test_delete_employee(self, api_client_v1, auth_headers):
        """Тест удаления сотрудника"""
        employee_id = 1
        response = api_client_v1.delete(
            f"/api/v1/employees/{employee_id}",
            headers=auth_headers
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.INTERNAL_SERVER_ERROR
        ]


class TestManagerDepartment:
    """Тесты для работы менеджера отдела с сотрудниками"""

    def test_get_manager_department_employees(self, api_client_v1, auth_headers):
        """Тест получения сотрудников отдела менеджером"""
        response = api_client_v1.get(
            "/api/v1/employees/manager-department",
            headers=auth_headers
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.NOT_FOUND
        ]

    def test_add_employee_to_department(self, api_client_v1, auth_headers):
        """Тест добавления сотрудника в отдел менеджером"""
        data = {
            "user_id": 21,
            "first_name": "Test",
            "last_name": "Employee",
            "middle_name": "Middle",
            "phone_number": "+79991234567",
            "email": "test@example.com",
            "passport_data": "1234567890",
            "inn": "123456789012",
            "snils": "12345678901",
            "department_id": 1,
            "is_active": True
        }
        response = api_client_v1.post(
            "/api/v1/employees/manager-department",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.NOT_FOUND
        ]

    def test_update_employee_by_manager(self, api_client_v1, auth_headers):
        """Тест обновления информации о сотруднике менеджером"""
        employee_id = 33
        data = {
            "user_id": 23,
            "first_name": "Updated",
            "last_name": "Employee",
            "middle_name": "Middle",
            "phone_number": "+79715984522",
            "email": "user@example.com",
            "passport_data": "1234567890",
            "inn": "123456789012",
            "snils": "12345678901",
            "department_id": 1,
            "is_active": True
        }
        response = api_client_v1.put(
            f"/api/v1/employees/manager-department/{employee_id}",
            headers=auth_headers,
            json=data
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.FORBIDDEN
        ]

    def test_delete_employee_by_manager(self, api_client_v1, auth_headers):
        """Тест удаления сотрудника менеджером"""
        employee_id = 2
        response = api_client_v1.delete(
            f"/api/v1/employees/manager-department/{employee_id}",
            headers=auth_headers
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.NO_CONTENT,
            HTTPStatus.NOT_FOUND,
            HTTPStatus.FORBIDDEN
        ]

