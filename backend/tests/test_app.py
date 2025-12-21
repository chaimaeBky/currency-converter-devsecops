import pytest
from unittest.mock import patch, Mock
from app import app



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



def test_rates_invalid_currency(client):
    """Test validation of invalid currency code for /rates"""
    with patch('requests.get'):
        response = client.get('/rates?base=USD1')
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'Invalid currency code' in data['message']


def test_rates_valid_currency(client):
    """Test valid currency code for /rates"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'base_code': 'EUR',
        'conversion_rates': {'USD': 1.18, 'GBP': 0.86}
    }
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates?base=EUR')
        assert response.status_code == 200
        data = response.get_json()
        assert data['base'] == 'EUR'


def test_convert_invalid_currency_from(client):
    """Test invalid 'from' currency for /convert"""
    with patch('requests.get'):
        response = client.get('/convert?from=USD1&to=EUR&amount=1')
        assert response.status_code == 400


def test_convert_invalid_currency_to(client):
    """Test invalid 'to' currency for /convert"""
    with patch('requests.get'):
        response = client.get('/convert?from=USD&to=EUR1&amount=1')
        assert response.status_code == 400


def test_convert_invalid_amount(client):
    """Test invalid amount parameter for /convert"""
    with patch('requests.get'):
        response = client.get('/convert?from=USD&to=EUR&amount=invalid')
        assert response.status_code == 400


def test_convert_negative_amount(client):
    """Test negative amount for /convert"""
    with patch('requests.get'):
        response = client.get('/convert?from=USD&to=EUR&amount=-1')
        assert response.status_code == 400


def test_convert_valid_request(client):
    """Test valid conversion request"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_result': 0.85,
        'conversion_rate': 0.85
    }
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/convert?from=USD&to=EUR&amount=100')
        assert response.status_code == 200
        data = response.get_json()
        assert data['from'] == 'USD'
        assert data['to'] == 'EUR'
        assert data['amount'] == 100
        assert data['converted'] == 0.85


def test_health_endpoint_exists(client):
    """Test health endpoint exists"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'

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
Also, you might need to add a conftest.py file if you don't have one. Create it in the same directory:

python
# conftest.py
import pytest
from app import app as flask_app


@pytest.fixture
def app():
    """Create Flask app fixture"""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    return flask_app


@pytest.fixture
def client(app):
    """Create test client fixture"""
    return app.test_client()
