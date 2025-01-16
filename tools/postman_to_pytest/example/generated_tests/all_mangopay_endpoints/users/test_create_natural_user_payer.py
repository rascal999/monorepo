"""
Test for creating a natural user with payer category.
"""
import pytest


@pytest.mark.dependency()
def test_create_natural_user_payer(api_session, env_vars, faker_vars, dynamic_vars):
    """Test creating a natural user with payer category."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users/natural"
    
    body = {
        "FirstName": faker_vars["$randomFirstName"],
        "LastName": faker_vars["$randomLastName"],
        "Email": faker_vars["$randomEmail"],
        "Address": {
            "AddressLine1": faker_vars["$randomStreetAddress"],
            "AddressLine2": faker_vars["$randomStreetName"],
            "City": "Paris",
            "Region": "Ile-de-France",
            "PostalCode": "75001",
            "Country": "FR"
        },
        "UserCategory": "PAYER",
        "TermsAndConditionsAccepted": False,
        "Tag": "Created using Mangopay API Postman Collection"
    }
    
    response = api_session.post(url, json=body)
    assert response.status_code == 200
    dynamic_vars["USER_NATURAL_PAYER"] = response.json()["Id"]
    return response
