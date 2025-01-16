"""
Test for creating a legal user with payer category.
"""
import pytest


@pytest.mark.dependency(name="create_legal_user_payer")
def test_create_legal_user_payer(api_session, env_vars, faker_vars, dynamic_vars):
    """Test creating a legal user with payer category."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users/legal"
    
    body = {
        "LegalPersonType": "BUSINESS",
        "Name": faker_vars["$randomCompanyName"],
        "LegalRepresentativeAddress": {
            "AddressLine1": faker_vars["$randomStreetAddress"],
            "AddressLine2": faker_vars["$randomStreetName"],
            "City": "Paris",
            "Region": "Ile-de-France",
            "PostalCode": "75001",
            "Country": "FR"
        },
        "LegalRepresentativeFirstName": faker_vars["$randomFirstName"],
        "LegalRepresentativeLastName": faker_vars["$randomLastName"],
        "Email": faker_vars["$randomEmail"],
        "UserCategory": "PAYER",
        "TermsAndConditionsAccepted": False,
        "Tag": "Created using Mangopay API Postman Collection"
    }
    
    response = api_session.post(url, json=body)
    assert response.status_code == 200
    dynamic_vars["USER_LEGAL_PAYER"] = response.json()["Id"]
