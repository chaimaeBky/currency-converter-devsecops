import pytest
from unittest.mock import patch, Mock
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config.update({"TESTING": True})
    with flask_app.test_client() as client:
        yield client


def test_fetch_conversion_rates(client):
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rates': {'USD': 1, 'EUR': 0.85, 'MAD': 10.0}
    }
    mock_response.raise_for_status = Mock()

    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates')
        assert response.status_code == 200
        data = response.get_json()
        assert 'conversion_rates' in data
        assert data['conversion_rates']['EUR'] == 0.85
        assert data['conversion_rates']['MAD'] == 10.0


def test_integration_currency_conversion(client):
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rates': {'USD': 1, 'EUR': 0.85}
    }
    mock_response.raise_for_status = Mock()

    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates')
        data = response.get_json()

        amount = 100
        from_currency = 'USD'
        to_currency = 'EUR'
        converted = (
            amount * data['conversion_rates'][to_currency]
            / data['conversion_rates'][from_currency]
        )
        assert converted == 85.0


def test_backend_handles_api_failure(client):
    with patch('requests.get', side_effect=Exception("API Failure")):
        response = client.get('/rates')
        assert response.status_code == 500 or b"error" in response.data
