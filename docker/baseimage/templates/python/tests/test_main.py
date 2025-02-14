import pytest
from main import app, App

def test_app_initialization():
    """Test that the app is initialized correctly"""
    assert isinstance(app, App)
    assert app.name == "APP_NAME"  # This will be replaced with actual project name

def test_app_logging_setup():
    """Test that logging can be set up"""
    logger = app.setup_logging()
    assert logger is not None
    assert app.logger is not None

def test_mask_sensitive_values():
    """Test the masking of sensitive values"""
    test_vars = {
        'API_KEY': '1234567890abcdef',
        'PUBLIC_URL': 'https://example.com',
        'DB_PASSWORD': 'secret123',
    }
    
    masked = app.mask_sensitive_values(test_vars)
    
    # API_KEY should be masked
    assert masked['API_KEY'] != test_vars['API_KEY']
    assert '*' in masked['API_KEY']
    
    # PUBLIC_URL should not be masked (contains URL)
    assert masked['PUBLIC_URL'] == test_vars['PUBLIC_URL']
    
    # DB_PASSWORD should be masked
    assert masked['DB_PASSWORD'] != test_vars['DB_PASSWORD']
    assert '*' in masked['DB_PASSWORD']