import requests

def validate_ticket_id(ticket_id):
    """Validate the ticket ID format"""
    if not ticket_id or not isinstance(ticket_id, str):
        return False
    # Basic format check: PROJECT-123
    parts = ticket_id.split('-')
    if len(parts) != 2:
        return False
    if not parts[0].isalpha() or not parts[1].isdigit():
        return False
    return True

def validate_url(url):
    """Basic URL validation"""
    if not url:
        return False
    try:
        response = requests.head(url)
        return True
    except:
        return False

def get_missing_credentials(jira_url, jira_token, jira_email):
    """Check for missing required credentials"""
    missing = []
    if not jira_url:
        missing.append('JIRA_URL')
    if not jira_token:
        missing.append('JIRA_TOKEN')
    if not jira_email:
        missing.append('JIRA_EMAIL')
    return missing