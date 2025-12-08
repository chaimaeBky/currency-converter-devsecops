#Tests de sécurité de l'application"""
import pytest
from unittest.mock import patch, Mock


def test_api_key_not_exposed_in_response(client):
    """CRITIQUE: Vérifier que la clé API n'est JAMAIS exposée"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'result': 'success',
        'conversion_rates': {'EUR': 0.85}
    }
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates')
        data_str = str(response.get_data())
        
        # La clé API ne devrait JAMAIS apparaître
        assert 'API_KEY' not in data_str
        assert '97f9dc6126138480ee6da5fb' not in data_str
        assert 'exchangerate-api.com/v6/' not in data_str


def test_cors_configured_properly(client):
    """Test que CORS est correctement configuré"""
    mock_response = Mock()
    mock_response.json.return_value = {'result': 'success', 'conversion_rates': {}}
    mock_response.raise_for_status = Mock()
    
    with patch('requests.get', return_value=mock_response):
        response = client.get('/rates', headers={'Origin': 'http://localhost:5173'})
        assert 'Access-Control-Allow-Origin' in response.headers


def test_no_debug_mode_in_production(app):
    """Test que le mode debug n'est pas activé en production"""
    assert app.debug is False
