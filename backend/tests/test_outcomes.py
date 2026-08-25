def test_outcomes_require_auth(client):
    assert client.get('/api/v1/outcomes/me').status_code == 401

def test_mentor_dashboard_requires_auth(client):
    assert client.get('/api/v1/dashboard/mentor').status_code == 401
