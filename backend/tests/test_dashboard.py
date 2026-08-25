def test_dashboard_requires_auth(client):
    assert client.get('/api/v1/dashboard/student').status_code == 401
