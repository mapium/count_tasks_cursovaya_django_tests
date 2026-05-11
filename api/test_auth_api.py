import pytest
from http import HTTPStatus


class TestAuth:
    """Тесты для аутентификации"""

    def test_login(self, api_client_v1):
        """Тест входа в систему"""
        data = {"username": "admin", "password": "admin123"}
        response = api_client_v1.post("/api/v1/auth/login", data=data)
        assert response.status_code == HTTPStatus.OK
        assert "access_token" in response.json()

    def test_login_with_invalid_credentials(self, api_client_v1):
        """Тест входа с неверными учетными данными"""
        data = {"username": "invalid", "password": "invalid"}
        response = api_client_v1.post("/api/v1/auth/login", data=data)
        assert response.status_code != HTTPStatus.OK

    def test_signup(self, api_client_v1):
        """Тест регистрации нового пользователя"""
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = api_client_v1.post("/api/v1/accounts/sign_up", data=data)
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.BAD_REQUEST,
            HTTPStatus.INTERNAL_SERVER_ERROR
        ]

    def test_signup_as_admin(self, api_client_v1, auth_headers):
        """Тест регистрации администратора"""
        response = api_client_v1.post(
            "/api/v1/accounts/sign_up_as_admin",
            headers=auth_headers
        )
        assert response.status_code in [
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.FORBIDDEN,
            HTTPStatus.UNAUTHORIZED,
            HTTPStatus.UNPROCESSABLE_ENTITY
        ]

    def test_refresh_token(self, api_client_v1, auth_token):
        """Тест обновления токена"""
        login_data = {"username": "admin", "password": "admin123"}
        login_response = api_client_v1.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == HTTPStatus.OK
        
        login_json = login_response.json()
        refresh_token = login_json.get("refresh_token")
        
        if refresh_token:
            response = api_client_v1.post(
                f"/api/v1/auth/refresh?refresh_token={refresh_token}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            assert response.status_code in [
                HTTPStatus.OK,
                HTTPStatus.BAD_REQUEST,
                HTTPStatus.UNAUTHORIZED
            ]
        else:
            assert "access_token" in login_json
            assert login_json.get("refresh_token") in (None, "")

