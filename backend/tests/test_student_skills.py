def test_skill_requires_auth(client):
    assert client.get('/api/v1/students/me/skills').status_code==401
