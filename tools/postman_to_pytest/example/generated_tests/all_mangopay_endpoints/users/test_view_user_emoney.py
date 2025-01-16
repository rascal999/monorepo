"""
Test for viewing user emoney information.
"""
import pytest


@pytest.mark.dependency(depends=["create_natural_user_owner"])
def test_view_user_emoney(api_session, env_vars, dynamic_vars):
    """Test viewing user emoney information."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users/{dynamic_vars['USER_NATURAL_OWNER']}/emoney"
    response = api_session.get(url)
    assert response.status_code == 200
