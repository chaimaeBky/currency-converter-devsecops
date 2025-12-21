import pytest
from unittest.mock import patch, Mock



def test_app_exists(app):
    """Test que l'application Flask existe"""
    assert app is not None


def test_app_is_testing(app):
    """Test que l'app est en mode testing"""
    assert app.config['TESTING'] is True


def test_get_rates_endpoint_exists(client):
    """Test que le endpoint /rates existe"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rates': {'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0}
    }
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates')
        assert response.status_code == 200


def test_rates_returns_json(client):
    """Test que /rates retourne du JSON"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rates': {'EUR': 0.85}
    }
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates')
        assert response.content_type == 'application/json'


def test_rates_contains_conversion_rates(client):
    """Test que la réponse contient des taux de conversion"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rates': {'EUR': 0.85, 'MAD': 10.0}
    }
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates')
        data = response.get_json()
        
        assert 'conversion_rates' in data
        assert data['conversion_rates']['EUR'] == 0.85


def test_cors_headers_present(client):
    """Test que les headers CORS sont présents"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rates': {'EUR': 0.85}
    }
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates')
        assert 'Access-Control-Allow-Origin' in response.headers

# Add these tests to test_app.py

def test_rates_api_key_missing(monkeypatch):
    """Test /rates when API key is not configured"""
    # Temporarily remove the API key
    import app
    monkeypatch.setattr(app, 'EXCHANGE_API_KEY', None)
    
    response = app.app.test_client().get('/rates')
    assert response.status_code == 503
    data = response.get_json()
    assert data['status'] == 'error'
    assert 'API key not configured' in data['message']


def test_convert_api_key_missing(monkeypatch):
    """Test /convert when API key is not configured"""
    # Temporarily remove the API key
    import app
    monkeypatch.setattr(app, 'EXCHANGE_API_KEY', None)
    
    response = app.app.test_client().get('/convert?from=USD&to=EUR&amount=1')
    assert response.status_code == 503
    data = response.get_json()
    assert data['status'] == 'error'
    assert 'API key not configured' in data['message']


def test_metrics_endpoint_exists(client):
    """Test Prometheus metrics endpoint exists"""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert 'text/plain' in response.content_type


def test_csrf_configuration(app):
    """Test CSRF is configured correctly"""
    # Test CSRF is enabled in config
    assert 'WTF_CSRF_ENABLED' in app.config
    assert app.config['WTF_CSRF_ENABLED'] is True
    
    # Test secret key is set
    assert 'SECRET_KEY' in app.config
    assert app.config['SECRET_KEY'] is not None


def test_cors_configuration():
    """Test CORS is configured"""
    from app import app
    # Check if CORS is properly set up
    response = app.test_client().get('/health')
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == '*'


def test_rates_exception_handling(client):
    """Test exception handling in /rates endpoint"""
    with patch('requests.get', side_effect=Exception("Network error")):
        response = client.get('/rates?base=USD')
        assert response.status_code == 500
        data = response.get_json()
        assert data['status'] == 'error'


def test_convert_exception_handling(client):
    """Test exception handling in /convert endpoint"""
    with patch('requests.get', side_effect=Exception("Network error")):
        response = client.get('/convert?from=USD&to=EUR&amount=1')
        assert response.status_code == 500
        data = response.get_json()
        assert data['status'] == 'error'



