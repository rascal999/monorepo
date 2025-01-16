"""
Test for viewing a specific user.
"""
import pytest


@pytest.mark.dependency(depends=["create_legal_user_owner"])
def test_view_user(api_session, env_vars, dynamic_vars):
    """Test viewing a specific user."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users/{dynamic_vars['USER_LEGAL_OWNER']}"
    response = api_session.get(url)
    assert response.status_code == 200
