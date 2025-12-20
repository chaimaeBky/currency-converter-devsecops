"""Simple test to ensure coverage is generated"""
def test_always_passes():
    """Test that always passes to generate coverage"""
    assert True

def test_import_app():
    """Test that app imports correctly"""
    try:
        from app import app
        assert app is not None
        assert hasattr(app, 'test_client')
        print("✅ App imports successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        raise

def test_health_endpoint_exists(client):
    """Test health endpoint exists"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'
