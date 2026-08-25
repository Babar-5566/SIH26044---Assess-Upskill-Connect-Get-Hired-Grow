def test_unauthenticated(client):
    assert client.get('/api/v1/students/me').status_code==401
