def test_jobs_requires_auth(client):
    assert client.get('/api/v1/jobs').status_code == 401
