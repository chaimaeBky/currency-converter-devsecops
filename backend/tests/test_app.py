
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
