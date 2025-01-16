"""
Test for updating a natural user with owner category.
"""
import pytest


@pytest.mark.dependency(depends=["generated_tests/all_mangopay_endpoints/users/test_create_natural_user_owner.py::test_create_natural_user_owner"])
def test_update_natural_user_owner(api_session, env_vars, faker_vars, dynamic_vars):
    """Test updating a natural user."""
    url = f"{env_vars['ENV_URL']}/v2.01/{env_vars['CLIENT_ID']}/users/natural/{dynamic_vars['USER_NATURAL_OWNER']}"
    
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
        "Birthday": 652117514,
        "CountryOfResidence": "FR",
        "Nationality": "FR",
        "UserCategory": "OWNER",
        "TermsAndConditionsAccepted": True,
        "Tag": "Created using Mangopay API Postman Collection"
    }
    
    response = api_session.put(url, json=body)
    assert response.status_code == 200
    dynamic_vars["USER_NATURAL_OWNER"] = response.json()["Id"]
    return response
