def test_resume_intelligence_requires_auth(client):
    response = client.post('/api/v1/resume-intelligence/analyze', params={'text':'Python project experience'})
    assert response.status_code == 401
