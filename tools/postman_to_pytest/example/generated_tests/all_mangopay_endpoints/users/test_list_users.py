"""
Test for listing all users.
"""
import pytest


@pytest.mark.dependency()
def test_list_users(api_session, env_vars):
    """Test listing all users."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users"
    response = api_session.get(url)
    assert response.status_code == 200
    return response
