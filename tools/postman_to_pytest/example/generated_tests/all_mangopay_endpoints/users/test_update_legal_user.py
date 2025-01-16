"""
Tests for updating a legal user.
"""
import pytest


@pytest.mark.dependency(name="test_create_legal_user_owner")
def test_create_legal_user_owner(api_session, env_vars, faker_vars, dynamic_vars):
    """Test creating a legal user with owner category."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users/legal"
    
    body = {
        "HeadquartersAddress": {
            "AddressLine1": faker_vars["$randomStreetAddress"],
            "AddressLine2": faker_vars["$randomStreetName"],
            "City": "Paris",
            "Region": "Ile-de-France",
            "PostalCode": "75001",
            "Country": "FR"
        },
        "LegalPersonType": "BUSINESS",
        "Name": faker_vars["$randomCompanyName"],
        "Email": faker_vars["$randomEmail"],
        "CompanyNumber": faker_vars["$randomInt"],
        "LegalRepresentativeAddress": {
            "AddressLine1": faker_vars["$randomStreetAddress"],
            "AddressLine2": faker_vars["$randomStreetName"],
            "City": "Paris",
            "Region": "Ile-de-France",
            "PostalCode": "75001",
            "Country": "FR"
        },
        "LegalRepresentativeBirthday": 652117514,
        "LegalRepresentativeCountryOfResidence": "FR",
        "LegalRepresentativeNationality": "FR",
        "LegalRepresentativeEmail": faker_vars["$randomEmail"],
        "LegalRepresentativeFirstName": faker_vars["$randomFirstName"],
        "LegalRepresentativeLastName": faker_vars["$randomLastName"],
        "UserCategory": "OWNER",
        "TermsAndConditionsAccepted": True,
        "Tag": "Created using Mangopay API Postman Collection"
    }
    
    response = api_session.post(url, json=body)
    assert response.status_code == 200
    dynamic_vars["USER_LEGAL_OWNER"] = response.json()["Id"]


@pytest.mark.dependency(depends=["test_create_legal_user_owner"])
def test_update_legal_user(api_session, env_vars, faker_vars, dynamic_vars):
    """Test updating a legal user."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users/legal/{dynamic_vars['USER_LEGAL_OWNER']}"
    
    body = {
        "HeadquartersAddress": {
            "AddressLine1": faker_vars["$randomStreetAddress"],
            "AddressLine2": faker_vars["$randomStreetName"],
            "City": "Paris",
            "Region": "Ile-de-France",
            "PostalCode": "75001",
            "Country": "FR"
        },
        "LegalPersonType": "BUSINESS",
        "Name": faker_vars["$randomCompanyName"],
        "Email": faker_vars["$randomEmail"],
        "CompanyNumber": faker_vars["$randomInt"],
        "LegalRepresentativeAddress": {
            "AddressLine1": faker_vars["$randomStreetAddress"],
            "AddressLine2": faker_vars["$randomStreetName"],
            "City": "Paris",
            "Region": "Ile-de-France",
            "PostalCode": "75001",
            "Country": "FR"
        },
        "LegalRepresentativeBirthday": 652117514,
        "LegalRepresentativeCountryOfResidence": "FR",
        "LegalRepresentativeNationality": "FR",
        "LegalRepresentativeEmail": faker_vars["$randomEmail"],
        "LegalRepresentativeFirstName": faker_vars["$randomFirstName"],
        "LegalRepresentativeLastName": faker_vars["$randomLastName"],
        "UserCategory": "OWNER",
        "TermsAndConditionsAccepted": True,
        "Tag": "Created using Mangopay API Postman Collection"
    }
    
    response = api_session.put(url, json=body)
    assert response.status_code == 200
