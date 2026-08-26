import pytest
from app import app, check_rate_limit, last_request_time
import time

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test that the index page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI Image Generator' in response.data

def test_about_route(client):
    """Test that the about page loads successfully."""
    response = client.get('/about')
    assert response.status_code == 200

def test_generate_requires_prompt(client):
    """Test that the generate endpoint requires a prompt."""
    # Reset rate limiting for this IP
    if '127.0.0.1' in last_request_time:
        del last_request_time['127.0.0.1']
        
    response = client.post('/generate', json={})
    assert response.status_code == 400
    assert b'Prompt is required' in response.data

def test_rate_limiting():
    """Test the rate limiting logic directly."""
    test_ip = "192.168.1.1"
    
    # First request should be allowed
    allowed, wait = check_rate_limit(test_ip)
    assert allowed == True
    assert wait == 0
    
    # Immediate second request should be blocked
    allowed, wait = check_rate_limit(test_ip)
    assert allowed == False
    assert wait > 0
    
    # After simulating time passing, should be allowed again
    last_request_time[test_ip] = time.time() - 3.0
    allowed, wait = check_rate_limit(test_ip)
    assert allowed == True
