import pytest
from page_analyzer import app  # Импортируем Flask-приложение


@pytest.fixture()
def client():
    """Создает тестовый клиент для тестирования API."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Проверяет, что главная страница возвращает 200 и 'Hello!'."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"Hello!"
