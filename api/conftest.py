import pytest
import httpx
from http import HTTPStatus
BASE_URL = "http://127.0.0.1:8001/"
@pytest.fixture(scope="session")
def api_client_v1():
    """предоставление HTTP-клиента для тестирования API"""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client

@pytest.fixture(scope="function") 
def auth_token(api_client_v1):
    """Получение токенааутентификации"""
    data = {"username": "admin", "password": "admin123"}
    resp = api_client_v1.post("/api/v1/auth/login", data=data)
    assert resp.status_code== HTTPStatus.OK, f"Authfailed: {resp.text}"
    token = resp.json()["access_token"]
    return token

@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Получениезаголовка авторизации"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="function")
def refresh_token(api_client_v1):
    """Получение токена из ответа логина для запроса refresh"""
    data = {"username": "admin", "password": "admin123"}
    resp = api_client_v1.post("/api/v1/auth/login", data=data)
    assert resp.status_code == HTTPStatus.OK, f"Auth failed: {resp.text}"
    return resp.json()["access_token"]

@pytest.fixture(scope="function") 
def auth_token_hr(api_client_v1):
    """Получение токенааутентификации"""
    data = {"username": "admin", "password": "admin123"}
    resp = api_client_v1.post("/api/v1/auth/login", data=data)
    assert resp.status_code== HTTPStatus.OK, f"Auth failed: {resp.text}"
    token = resp.json()["access_token"]
    return token

@pytest.fixture(scope="function")
def auth_headers_hr(auth_token_hr):
    """Получениезаголовка авторизации"""
    return {"Authorization": f"Bearer {auth_token_hr}"}


